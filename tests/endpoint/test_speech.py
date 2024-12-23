"""Tests for the speech endpoints."""

import array
import tempfile
import wave
from collections.abc import Generator
from typing import Any

import ffmpeg
import pytest
import pytest_mock
from cloai import openai_api
from fastapi import status, testclient

from tests.endpoint import conftest


@pytest.fixture()
def wav_file() -> Generator[str, Any, None]:
    """Returns a path to a temporary wav file."""
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        wav = wave.open(f, "w")
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(array.array("h", [0] * 44100).tobytes())
        wav.close()
        yield f.name


@pytest.fixture()
def mp3_file(wav_file: str) -> Generator[str, Any, None]:
    """Returns a path to a temporary mp3 file."""
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        ffmpeg.input(wav_file).output(f.name).overwrite_output().run()
        yield f.name


@pytest.fixture()
def files(wav_file: str, mp3_file: str) -> dict[str, str]:
    """Workaround for pytest.mark.parametrize not supporting fixtures."""
    return {"wav": wav_file, "mp3": mp3_file}


@pytest.mark.parametrize("file_type", ["wav", "mp3"])
def test_transcribe(
    mocker: pytest_mock.MockerFixture,
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
    files: dict[str, str],
    file_type: str,
) -> None:
    """Tests the transcribe endpoint."""
    expected_transcription = "Expected transcription"
    mock_stt_run = mocker.patch.object(
        openai_api.SpeechToText,
        "run",
        return_value=expected_transcription,
    )

    response = client.post(
        endpoints.POST_SPEECH_TRANSCRIBE,
        files={"audio": open(files[file_type], "rb")},  # noqa: SIM115, PTH123
        data={"language": "en"},
    )

    assert response.status_code == status.HTTP_200_OK
    mock_stt_run.assert_called_once()
    assert response.json() == expected_transcription
