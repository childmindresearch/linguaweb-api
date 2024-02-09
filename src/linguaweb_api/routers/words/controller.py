"""Business logic for the text router."""
import logging

import fastapi
import sqlalchemy
from botocore import errorfactory
from fastapi import status
from sqlalchemy import orm

from linguaweb_api.core import config, models
from linguaweb_api.microservices import s3

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


async def get_all_word_ids(
    language: str | None,
    age: int | None,
    session: orm.Session,
) -> list[int]:
    """Returns all word IDs.

    Args:
        language: The language of the words.
        age: The age of the target audience.
        session: The database session.

    Returns:
        The IDs of all words.

    """
    logger.debug("Getting all word IDs.")
    query = sqlalchemy.select(models.Word.id)
    if language:
        query = query.where(models.Word.language == language)
    if age:
        query = query.where(models.Word.age == age)
    words = session.execute(query)

    return [word.id for word in words]


async def get_word(identifier: int, session: orm.Session) -> models.Word:
    """Returns the description of a random word.

    Args:
        identifier: The id of the word.
        session: The database session.

    Returns:
        The description of the word.

    Raises:
        fastapi.HTTPException: 404 If the word was not found in the database.

    """
    logger.debug("Getting word description.")
    word = session.query(models.Word).filter_by(id=identifier).first()
    if not word:
        logger.warning("Word not found in database.")
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found.",
        )
    return word


async def check_word(
    word_id: int,
    word: str,
    session: orm.Session,
) -> bool:
    """Checks whether a word was guessed correctly.

    Args:
        word_id: The ID of the word to check.
        word: The word to check.
        session: The database session.

    Returns:
        bool: Whether the word was guessed correctly.

    Raises:
        fastapi.HTTPException: 404 If the word was not found in the database.

    Notes:
        Case insensitive.
    """
    logger.debug("Checking word: %s", word)
    word_model = session.query(models.Word).filter_by(id=word_id).first()
    if not word_model:
        logger.warning("Word ID not found in database.")
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word ID not found.",
        )
    return _sanitize_word(word) == _sanitize_word(word_model.word)


def download_audio(identifier: int, session: orm.Session, s3_client: s3.S3) -> bytes:
    """Downloads the audio of a word.

    Args:
        identifier: The id of the word.
        session: The database session.
        s3_client: The S3 client to use.

    Returns:
        The audio bytes.
    """
    logger.debug("Downloading audio.")
    word = session.query(models.Word).filter_by(id=identifier).first()
    if not word:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio not found.",
        )
    try:
        return s3_client.read(word.s3_file.s3_key)
    except errorfactory.ClientError as exception_info:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio not found.",
        ) from exception_info


def _sanitize_word(word: str) -> str:
    """Sanitizes a word.

    Removes leading and trailing whitespace, converts to lowercase
    and removes punctuation.

    Args:
        word: The word to sanitize.

    Returns:
        The sanitized word.
    """
    return word.lower().strip().strip(".,?!;:'\"")
