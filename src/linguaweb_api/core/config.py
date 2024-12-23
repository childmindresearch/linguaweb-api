"""Settings for the API."""

import enum
import functools
import logging
import pathlib
from typing import NotRequired, TypedDict

import pydantic
import pydantic_settings

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"


class Voices(str, enum.Enum):
    """A class representing the voices for the Text-To-Speech model."""

    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"


class TTSModels(str, enum.Enum):
    """Supported Text-To-Speech models."""

    TTS1 = "tts-1"


class STTModels(str, enum.Enum):
    """Supported Speech-To-Text models."""

    WHISPER1 = "whisper-1"


class GPTModels(str, enum.Enum):
    """Supported GPT models."""

    GPT4_1106_Preview = "gpt-4-1106-preview"
    GPT4 = "gpt-4"

    GPT35_turbo_1106 = "gpt3-5-turbo-1106"
    GPT35_turbo = "gpt3-5-turbo"


class ExternalDocumentation(TypedDict):
    """OpenAPI external documentation definition."""

    description: str
    url: str


class OpenApiTag(TypedDict):
    """OpenAPI tag definition."""

    name: str
    description: str
    externalDocs: NotRequired[ExternalDocumentation]


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

    API_KEY: pydantic.SecretStr = pydantic.Field(
        ...,
        json_schema_extra={"env": "API_KEY"},
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
    OPENAI_VOICE: Voices = pydantic.Field(
        "onyx",
        json_schema_extra={"env": "OPENAI_VOICE"},
    )
    OPENAI_GPT_MODEL: GPTModels = pydantic.Field(
        "gpt-4-1106-preview",
        json_schema_extra={"env": "OPENAI_GPT_MODEL"},
    )
    OPENAI_TTS_MODEL: TTSModels = pydantic.Field(
        "tts-1",
        json_schema_extra={"env": "OPENAI_TTS_MODEL"},
    )
    OPENAI_STT_MODEL: STTModels = pydantic.Field(
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
    POSTGRES_DATABASE: str = pydantic.Field(
        "postgres",
        json_schema_extra={"env": "POSTGRES_DATABASE"},
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
