"""View definitions for the speech router."""

import logging

import fastapi
from fastapi import status

from linguaweb_api.core import config
from linguaweb_api.routers.speech import controller

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

router = fastapi.APIRouter(prefix="/speech", tags=["speech"])


@router.post(
    "/transcribe",
    response_model=str,
    status_code=status.HTTP_200_OK,
    summary="Transcribes an audio file and returns the transcription.",
    description="""Uses OpenAI's Whisper API to transcribe the provided audio. Maximum
        allowed file size is 1 MB, and the audio file must be in a format that ffmpeg
        can convert to mp3.""",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "The audio file must have a filename.",
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "description": "The audio file size exceeds the maximum allowed size.",
        },
    },
)
async def transcribe(
    audio: fastapi.UploadFile = fastapi.File(...),
    language: str = fastapi.Form(...),
) -> str:
    """Transcribes audio using OpenAI's Whisper API.

    Args:
        audio: The audio file.
        language: The language of the audio.

    Returns:
        The transcription of the audio as a string.
    """
    logger.debug("Transcribing audio.")
    transcription = controller.transcribe(audio, language=language)
    logger.debug("Transcribed audio.")
    return await transcription
