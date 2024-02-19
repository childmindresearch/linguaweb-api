"""Tests for the admin endpoints."""
import pathlib
from collections.abc import Generator

import moto
import pytest
import pytest_mock
from fastapi import status, testclient

import linguaweb_api
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


def test_add_word_no_auth(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the add word endpoint without authentication."""
    response = client.post(endpoints.POST_ADD_WORD, data={"word": "test_word"})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_word(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the add word endpoint."""
    response = client.post(
        endpoints.POST_ADD_WORD,
        data={"word": "test_word"},
        headers={"x-api-key": "test"},
    )
    expected_keys = {
        "id",
        "synonyms",
        "antonyms",
        "jeopardy",
        "description",
        "word",
        "language",
    }

    assert response.status_code == status.HTTP_201_CREATED
    assert all(item in response.json() for item in expected_keys)


def test_add_word_already_exists(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the add word endpoint when the word already exists."""
    client.post(
        endpoints.POST_ADD_WORD,
        data={"word": "test_word"},
        headers={"x-api-key": "test"},
    )
    expected_keys = {
        "id",
        "synonyms",
        "antonyms",
        "jeopardy",
        "description",
        "word",
        "language",
    }

    response = client.post(
        endpoints.POST_ADD_WORD,
        data={"word": "test_word"},
        headers={"x-api-key": "test"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert set(response.json().keys()) == expected_keys


def test_add_preset_words_no_auth(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the add preset words endpoint without authentication."""
    response = client.post(endpoints.POST_ADD_PRESET_WORDS)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_preset_words(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the add preset words endpoint."""
    max_words = 2
    word_files = [
        pathlib.Path(linguaweb_api.__file__).parent
        / "data"
        / f"default_words_{language}.txt"
        for language in ("en-US", "nl-NL", "fr-FR")
    ]
    words = set()
    for word_file in word_files:
        with word_file.open() as file:
            words.update(file.read().splitlines()[:max_words])

    response = client.post(
        endpoints.POST_ADD_PRESET_WORDS,
        data={"max_words": str(max_words)},
        headers={"x-api-key": "test"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert {word["word"] for word in response.json()} == words
