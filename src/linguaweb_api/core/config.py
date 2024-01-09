"""Settings for the API."""
import functools
import logging
import pathlib
from typing import NotRequired, TypedDict

import pydantic
import pydantic_settings

from linguaweb_api.microservices import openai_constants

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"


class Settings(pydantic_settings.BaseSettings):  # type: ignore[valid-type, misc]
    """Settings for the API."""

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="LWAPI_",
        env_file_encoding="utf-8",
    )

    LOGGER_NAME: str = pydantic.Field("LinguaWeb API")
    LOGGER_VERBOSITY: int | None = pydantic.Field(
        logging.DEBUG,
        json_schema_extra={"env": "LOGGER_VERBOSITY"},
    )

    ENVIRONMENT: str = pydantic.Field(
        "development",
        json_schema_extra={"env": "ENVIRONMENT"},
    )

    PROMPT_FILE: pathlib.Path = pydantic.Field(
        DATA_DIR / "prompts.yaml",
        json_schema_extra={"env": "PROMPT_FILE"},
    )
    OPENAI_API_KEY: pydantic.SecretStr = pydantic.Field(
        ...,
        json_schema_extra={"env": "OPENAI_API_KEY"},
    )
    OPENAI_VOICE: openai_constants.Voices = pydantic.Field(
        "onyx",
        json_schema_extra={"env": "OPENAI_VOICE"},
    )
    OPENAI_GPT_MODEL: openai_constants.GPTModels = pydantic.Field(
        "gpt-4-1106-preview",
        json_schema_extra={"env": "OPENAI_GPT_MODEL"},
    )
    OPENAI_TTS_MODEL: openai_constants.TTSModels = pydantic.Field(
        "tts-1",
        json_schema_extra={"env": "OPENAI_TTS_MODEL"},
    )
    OPENAI_STT_MODEL: openai_constants.STTModels = pydantic.Field(
        "whisper-1",
        json_schema_extra={"env": "OPENAI_STT_MODEL"},
    )

    S3_ENDPOINT_URL: str | None = pydantic.Field(
        None,
        json_schema_extra={"env": "S3_ENDPOINT_URL"},
    )
    S3_BUCKET_NAME: str = pydantic.Field(
        "linguaweb",
        json_schema_extra={"env": "S3_BUCKET_NAME"},
    )
    S3_ACCESS_KEY: pydantic.SecretStr = pydantic.Field(
        ...,
        json_schema_extra={"env": "S3_ACCESS_KEY"},
    )
    S3_SECRET_KEY: pydantic.SecretStr = pydantic.Field(
        ...,
        json_schema_extra={"env": "S3_SECRET_KEY"},
    )
    S3_REGION: str = pydantic.Field(
        "us-east-1",
        json_schema_extra={"env": "S3_REGION"},
    )

    POSTGRES_URL: str = pydantic.Field(
        "localhost:5432",
        json_schema_extra={"env": "POSTGRES_HOST"},
    )
    POSTGRES_USER: pydantic.SecretStr = pydantic.Field(
        "postgres",
        json_schema_extra={"env": "POSTGRES_USER"},
    )
    POSTGRES_PASSWORD: pydantic.SecretStr = pydantic.Field(
        "postgres",
        json_schema_extra={"env": "POSTGRES_PASSWORD"},
    )

    SQLITE_FILE: str = pydantic.Field(
        "linguaweb.sqlite",
        json_schema_extra={"env": "SQLITE_FILE"},
    )


@functools.lru_cache
def get_settings() -> Settings:
    """Cached fetcher for the API settings.

    Returns:
        The settings for the API.
    """
    return Settings()  # type: ignore[call-arg]


def initialize_logger() -> None:
    """Initializes the logger for the API."""
    settings = get_settings()
    logger = logging.getLogger(settings.LOGGER_NAME)
    if settings.LOGGER_VERBOSITY is not None:
        logger.setLevel(settings.LOGGER_VERBOSITY)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)s - %(funcName)s - %(message)s",  # noqa: E501
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class ExternalDocumentation(TypedDict):
    """OpenAPI external documentation definition."""

    description: str
    url: str


class OpenApiTag(TypedDict):
    """OpenAPI tag definition."""

    name: str
    description: str
    externalDocs: NotRequired[ExternalDocumentation]


def open_api_specification() -> list[OpenApiTag]:
    """Returns the OpenAPI specification tags.

    Returns:
        list[OpenApiTag]: A list of OpenApiTag objects representing
            the tags in the OpenAPI specification.
    """
    return [
        {
            "name": "admin",
            "description": "Operations reserved for administrators.",
        },
        {
            "name": "health",
            "description": "Operations related to the health of the API.",
        },
        {
            "name": "speech",
            "description": "Operations related to speech transcription.",
        },
        {
            "name": "words",
            "description": "Operations related to words.",
        },
    ]
