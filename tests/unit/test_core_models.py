"""Tests for the BaseTable settings of SQL tables."""

import datetime
import time

import pytest
import sqlalchemy
from sqlalchemy import create_engine, orm

from linguaweb_api.core import models

Base = orm.declarative_base()


class ConcreteTable(Base, models.BaseTable):  # type: ignore[misc,valid-type]
    """A concrete table implementation for testing purposes."""

    __tablename__ = "concrete_table"


@pytest.fixture()
def engine() -> sqlalchemy.Engine:
    """Returns a SQLAlchemy engine for testing."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture()
def session(engine: sqlalchemy.Engine) -> orm.session.Session:
    """Returns a SQLAlchemy session for testing."""
    Base.metadata.create_all(engine)
    return orm.sessionmaker(bind=engine)()


def test_id_autoincrements(session: orm.session.Session) -> None:
    """Tests if the 'id' field autoincrements correctly."""
    entry1 = ConcreteTable()
    session.add(entry1)
    session.commit()

    entry2 = ConcreteTable()
    session.add(entry2)
    session.commit()

    assert entry1.id + 1 == entry2.id, "IDs should autoincrement by 1."


def test_time_created_set_on_creation(session: orm.session.Session) -> None:
    """Tests if 'time_created' is set automatically upon creation."""
    entry = ConcreteTable()
    session.add(entry)
    session.commit()

    assert isinstance(
        entry.time_created,
        datetime.datetime,
    ), "'time_created' should be a datetime object."


def test_time_updated_set_on_creation(session: orm.session.Session) -> None:
    """Tests if 'time_updated' is set automatically upon creation."""
    entry = ConcreteTable()
    session.add(entry)
    session.commit()

    assert isinstance(
        entry.time_updated,
        datetime.datetime,
    ), "'time_updated' should be a datetime object."


def test_time_updated_changes_on_update(session: orm.session.Session) -> None:
    """Tests if 'time_updated' changes when the record is updated."""
    entry = ConcreteTable()
    session.add(entry)
    session.commit()

    initial_time_updated = entry.time_updated
    time.sleep(1)
    entry.id = 999  # Dummy update
    session.commit()

    assert (
        entry.time_updated > initial_time_updated
    ), "'time_updated' should be greater after an update."
