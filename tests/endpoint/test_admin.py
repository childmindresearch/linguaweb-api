"""Tests for the admin endpoints."""
from collections.abc import Generator

import moto
import pytest
import pytest_mock
from fastapi import status, testclient

from linguaweb_api.core import dictionary
from tests.endpoint import conftest


class TextTask:
    """Mocked TextTask class."""

    def __init__(self) -> None:
        """Initializes a new instance of the TextTask class."""
        self.word_description = "test_description"
        self.word_synonyms = "test_synonym"
        self.word_antonyms = "test_antonym"
        self.word_jeopardy = "test_jeopardy"


@pytest.fixture(autouse=True)
def _mock_services(mocker: pytest_mock.MockerFixture) -> Generator[None, None, None]:
    """Mocks the calls to the microservices."""
    with moto.mock_s3():
        mocker.patch(
            "linguaweb_api.routers.admin.controller._get_text_tasks",
            return_value=TextTask(),
        )
        mocker.patch(
            "linguaweb_api.routers.admin.controller._get_listening_task",
            return_value=b"test_bytes",
        )
        yield


def test_add_word(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the add word endpoint."""
    response = client.post(endpoints.POST_ADD_WORD, data={"word": "test_word"})
    expected_keys = {
        "synonyms",
        "antonyms",
        "jeopardy",
        "description",
        "word",
        "s3_key",
    }

    assert response.status_code == status.HTTP_201_CREATED
    assert all(item in response.json() for item in expected_keys)


def test_add_word_already_exists(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the add word endpoint when the word already exists."""
    client.post(endpoints.POST_ADD_WORD, data={"word": "test_word"})

    response = client.post(endpoints.POST_ADD_WORD, data={"word": "test_word"})

    assert response.status_code == status.HTTP_409_CONFLICT


def test_add_preset_words(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the add preset words endpoint."""
    response = client.post(endpoints.POST_ADD_PRESET_WORDS)
    words = dictionary.read_words()

    assert response.status_code == status.HTTP_201_CREATED
    assert [word["word"] for word in response.json()] == words


def test_add_preset_words_already_exist(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the add preset words endpoint when the words already exist."""
    client.post(endpoints.POST_ADD_PRESET_WORDS)

    response = client.post(endpoints.POST_ADD_PRESET_WORDS)

    assert response.status_code == status.HTTP_409_CONFLICT
