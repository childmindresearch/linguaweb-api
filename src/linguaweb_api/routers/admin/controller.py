"""Controller for the listening router."""
import asyncio
import logging
import pathlib
from typing import Literal, NamedTuple

import fastapi
import pydantic
import yaml
from cloai import openai_api
from fastapi import status
from sqlalchemy import orm

from linguaweb_api.core import config, models
from linguaweb_api.microservices import s3

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME
OPENAI_VOICE = settings.OPENAI_VOICE
OPENAI_API_KEY = settings.OPENAI_API_KEY
PROMPT_FILE = settings.PROMPT_FILE
logger = logging.getLogger(LOGGER_NAME)


async def add_word(
    word: str,
    session: orm.Session,
    s3_client: s3.S3,
    language: Literal["en", "nl", "fr"] = "en",
) -> models.Word:
    """Adds a word to the database.

    Args:
        word: The word to add.
        session: The database session.
        s3_client: The S3 client to use.
        language: The language of the word.

    Returns:
        The word model.
    """
    logger.debug("Adding word.")
    word_model = session.query(models.Word).filter_by(word=word).first()
    if word_model:
        return word_model

    logger.debug("Word does not exist in database.")
    text_tasks_promise = _get_text_tasks(word, language)
    listening_bytes_promise = _get_listening_task(word)
    s3_key = f"{word}_{OPENAI_VOICE.value}_{language}.mp3"

    text_tasks, listening_bytes = await asyncio.gather(
        text_tasks_promise,
        listening_bytes_promise,
    )

    logger.debug("Creating new word.")
    existing_s3 = session.query(models.S3File).filter_by(s3_key=s3_key).first()
    if not existing_s3:
        existing_s3 = models.S3File(s3_key=s3_key)
        session.add(existing_s3)

    new_word = models.Word(
        word=word,
        description=text_tasks.word_description,
        synonyms=text_tasks.word_synonyms,
        antonyms=text_tasks.word_antonyms,
        jeopardy=text_tasks.word_jeopardy,
        language=language,
        s3_file=existing_s3,
    )
    s3_client.create(key=s3_key, data=listening_bytes)
    session.add(new_word)
    session.commit()
    logger.debug("Added word.")
    return new_word


async def add_preset_words(
    session: orm.Session,
    s3_client: s3.S3,
    max_words: int | None,
) -> list[models.Word]:
    """Adds preset words to the database.

    Args:
        session: The database session.
        s3_client: The S3 client to use.
        max_words: The maximum number of words to add per language. If None,
            all words will be added.

    Returns:
        The word models.
    """
    logger.debug("Adding preset words.")
    promises = []

    languages = ("en", "nl", "fr")
    for language in languages:
        preset_words = _read_words(language)  # type: ignore[arg-type]
        if max_words:
            preset_words = preset_words[:max_words]

        promises.extend(
            [
                add_word(word, session, s3_client, language=language)  # type: ignore[arg-type]
                for word in preset_words
            ],
        )

    word_models = await asyncio.gather(*promises)
    logger.debug("Added preset words.")
    return word_models


class _TextTasks(NamedTuple):
    """Named tuple for the text tasks."""

    word_description: str
    word_synonyms: str
    word_antonyms: str
    word_jeopardy: str


async def _get_text_tasks(word: str, language: Literal["en", "nl", "fr"]) -> _TextTasks:
    """Runs GPT to get text tasks.

    Args:
        word: The word to get text tasks for.
        language: The language to use.

    Returns:
        The text tasks.
    """
    logger.debug("Running GPT.")
    gpt = openai_api.ChatCompletion(api_key=OPENAI_API_KEY)
    prompts = _Prompts.load()
    if prompts.system is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System prompts not loaded.",
        )

    gpt_calls = {
        name: gpt.run(user_prompt=word, system_prompt=prompts.system[language][name])
        for name in _TextTasks._fields
    }

    results = {key: await response for key, response in gpt_calls.items()}
    return _TextTasks(**results)


async def _get_listening_task(word: str) -> bytes:
    """Fetches audio for a given word from OpenAI.

    Args:
        word: The word to fetch audio for.

    Returns:
        The audio bytes and the S3 key.
    """
    tts = openai_api.TextToSpeech(api_key=OPENAI_API_KEY)
    return await tts.run(word, voice=OPENAI_VOICE.value)


class _Prompts(pydantic.BaseModel):
    """A class containing OpenAI Prompts."""

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    system: dict[str, dict[str, str]] | None
    user: dict[str, dict[str, str]] | None

    @classmethod
    def load(cls, path: pathlib.Path = PROMPT_FILE) -> "_Prompts":
        """Loads prompts from a YAML file.

        Args:
            path: The path to the YAML file.

        Returns:
            The prompts.
        """
        with path.open("r", encoding="utf-8") as prompt_file:
            prompts = yaml.safe_load(prompt_file)

        return cls(**prompts)


def _read_words(language: Literal["en", "nl", "fr"]) -> list[str]:
    """Reads the words from the dictionary file."""
    dictionary_file = (
        pathlib.Path(__file__).parent.parent.parent
        / "data"
        / f"default_words_{language}.txt"
    )

    with dictionary_file.open() as file:
        return file.read().splitlines()
