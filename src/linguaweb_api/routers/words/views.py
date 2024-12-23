"""View definitions for the text router."""

import logging

import fastapi
from fastapi import status
from sqlalchemy import orm

from linguaweb_api.core import config
from linguaweb_api.microservices import s3, sql
from linguaweb_api.routers.words import controller, schemas

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

router = fastapi.APIRouter(prefix="/words", tags=["words"])


@router.get(
    "",
    response_model=list[int],
    status_code=status.HTTP_200_OK,
    summary="Returns all word IDs.",
    description="""Returns the IDs of all words in the database.""",
)
async def get_all_word_ids(
    language: str | None = fastapi.Query(
        None,
        title="The language of the words.",
        description="The language of the words.",
    ),
    age: int | None = fastapi.Query(
        None,
        title="The age of the target audience.",
        description="The age of the target audience.",
    ),
    session: orm.Session = fastapi.Depends(sql.get_session),
) -> list[int]:
    """Returns all word IDs.

    Args:
        language: The language of the words.
        age: The age of the target audience.
        session: The database session.
    """
    logger.debug("Getting all word IDs.")
    word_ids = await controller.get_all_word_ids(language, age, session)
    logger.debug("Got all word IDs.")
    return word_ids


@router.get(
    "/{identifier}",
    response_model=schemas.WordData,
    status_code=status.HTTP_200_OK,
    summary="Returns the data of a word.",
    description="""Returns the complete SQL model of a word.""",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Word not found.",
        },
    },
)
async def get_word(
    identifier: int = fastapi.Path(..., title="The id of the word."),
    session: orm.Session = fastapi.Depends(sql.get_session),
) -> schemas.WordData:
    """Returns the description of a random word.

    Args:
        identifier: The id of the word.
        session: The database session.
    """
    logger.debug("Getting word description.")
    text_task = await controller.get_word(identifier, session)
    logger.debug("Got word description.")
    return text_task


@router.post(
    "/check/{word_id}",
    status_code=status.HTTP_200_OK,
    summary="Checks whether a guessed word is correct.",
    description="Given an ID and a guessed word, checks if the guess is correct.",
)
async def check_word(
    word_id: int = fastapi.Path(..., title="The ID of the word to check."),
    word: str = fastapi.Form(..., title="The information to check."),
    session: orm.Session = fastapi.Depends(sql.get_session),
) -> bool:
    """Checks attributes of a word.

    Args:
        word_id: The ID of the word to check.
        word: The information to check.
        session: The database session.
    """
    logger.debug("Checking word.")
    is_correct = await controller.check_word(word_id, word, session)
    logger.debug("Checked word.")
    return is_correct


@router.get(
    "/download/{identifier}",
    status_code=status.HTTP_200_OK,
    summary="Returns the audio of a word.",
    description="Downloads the audio file for a specific word by its ID.",
)
async def get_audio(
    identifier: int = fastapi.Path(..., title="The id of the word."),
    session: orm.Session = fastapi.Depends(sql.get_session),
    s3_client: s3.S3 = fastapi.Depends(s3.S3),
) -> fastapi.Response:
    """Returns the audio of a word.

    Args:
        identifier: The id of the word.
        session: The database session.
        s3_client: The S3 client to use.
    """
    logger.debug("Downloading audio.")
    audio_bytes = controller.download_audio(identifier, session, s3_client)
    logger.debug("Downloaded audio.")

    return fastapi.Response(audio_bytes, media_type="audio/mp3")
