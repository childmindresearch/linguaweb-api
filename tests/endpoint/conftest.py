"""Fixtures and configurations for testing the endpoints of the CTK API."""

import enum

import pytest
import sqlalchemy
from fastapi import testclient
from sqlalchemy import orm

from linguaweb_api import main
from linguaweb_api.microservices import sql

API_ROOT = "/api/v1"


class Endpoints(str, enum.Enum):
    """Enum class that represents the available endpoints for the API."""

    POST_ADD_WORD = f"{API_ROOT}/admin/add_word"
    POST_ADD_PRESET_WORDS = f"{API_ROOT}/admin/add_preset_words"

    GET_WORD = f"{API_ROOT}/words/{{word_id}}"
    GET_ALL_WORD_IDS = f"{API_ROOT}/words"
    GET_AUDIO = f"{API_ROOT}/words/download/{{audio_id}}"
    POST_CHECK_WORD = f"{API_ROOT}/words/check/{{word_id}}"

    POST_SPEECH_TRANSCRIBE = f"{API_ROOT}/speech/transcribe"

    GET_HEALTH = f"{API_ROOT}/health"
    GET_CONNECTIVITY = f"{API_ROOT}/health/connectivity"


@pytest.fixture()
def endpoints() -> type[Endpoints]:
    """Returns the Endpoints enum class."""
    return Endpoints


@pytest.fixture()
def client() -> testclient.TestClient:
    """Returns a test client for the API."""
    return testclient.TestClient(main.app)


@pytest.fixture(autouse=True, scope="session")
def _start_database() -> None:
    """Starts the database."""
    main.database.create_database()


@pytest.fixture()
def session() -> orm.Session:
    """Returns a database session."""
    return next(sql.get_session())


@pytest.fixture(autouse=True)
def _clear_tables(session: orm.Session) -> None:
    """Clear all tables by deleting all their rows.

    Args:
        session: The database session.
    """
    base = orm.declarative_base()
    metadata = sqlalchemy.MetaData()
    metadata.reflect(bind=session.get_bind())
    base.metadata = metadata

    for table in reversed(metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
