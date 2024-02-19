"""Admin views."""
import logging

import fastapi
from fastapi import status
from sqlalchemy import orm

from linguaweb_api.core import config, models, security
from linguaweb_api.microservices import s3, sql
from linguaweb_api.routers.admin import controller, schemas

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

router = fastapi.APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[fastapi.Depends(security.check_api_key)],
)


@router.post(
    "/add_word",
    response_model=schemas.Word,
    status_code=status.HTTP_201_CREATED,
    summary="Adds a word to the database.",
    description="""Adds a word to the database. This will also perform all the OpenAI
    calls to create the word's tasks.""",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Word already exists in database.",
        },
    },
)
async def add_word(
    word: str = fastapi.Form(..., title="The word to add."),
    session: orm.Session = fastapi.Depends(sql.get_session),
    s3_client: s3.S3 = fastapi.Depends(s3.S3),
) -> schemas.Word:
    """Adds a word to the database.

    Args:
        word: The word to add.
        session: The database session.
        s3_client: The S3 client to use.
    """
    logger.debug("Adding word.")
    word_model = await controller.add_word(word, session, s3_client)
    logger.debug("Added word.")
    return word_model


@router.post(
    "/add_preset_words",
    response_model=list[schemas.Word],
    status_code=status.HTTP_201_CREATED,
    summary="Adds preset words to the database.",
    description="Wrapper around the add_words function that adds all preset words.",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "All preset words already exist in database.",
        },
    },
)
async def add_preset_words(
    session: orm.Session = fastapi.Depends(sql.get_session),
    s3_client: s3.S3 = fastapi.Depends(s3.S3),
    max_words: int | None = fastapi.Form(
        None,
        title="The maximum number of words to add per language.",
        description="The maximum number of words to add per language.",
    ),
) -> list[models.Word]:
    """Adds preset words to the database.

    Args:
        session: The database session.
        s3_client: The S3 client to use.
        max_words: The maximum number of words to add per language. If None,
            adds all words.
    """
    logger.debug("Adding preset words.")
    word_models = await controller.add_preset_words(session, s3_client, max_words)
    logger.debug("Added preset words.")
    return word_models
