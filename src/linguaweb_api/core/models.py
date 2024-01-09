"""Basic settings for all SQL tables."""
import datetime
from typing import Any

import sqlalchemy
from sqlalchemy import orm, types

from linguaweb_api.microservices import sql


class BaseTable(sql.Base):
    """Basic settings of a table. Contains an id, time_created, and time_updated."""

    __abstract__ = True

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
    time_created: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.func.now(),
    )
    time_updated: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    )


class CommaSeparatedList(types.TypeDecorator):
    """A custom SQLAlchemy for comma separated lists."""

    impl = sqlalchemy.String(1024)

    def process_bind_param(self, value: Any | None, _dialect: Any) -> str | None:  # noqa: ANN401
        """Converts a list of strings to a comma separated string.

        Args:
            value: The list of strings or a comma separated string.
            dialect: The dialect.

        Returns:
            str | None: The comma separated string.
        """
        if value is None:
            return None
        if isinstance(value, list):
            return ",".join(value)
        return value

    def process_result_value(
        self,
        value: Any | None,  # noqa: ANN401
        _dialect: Any,  # noqa: ANN401
    ) -> list[str] | None:
        """Converts a comma separated string to a list of strings.

        Args:
            value: The comma separated string.
            dialect: The dialect.

        Returns:
            list[str]: The list of strings.
        """
        if value is None:
            return None
        return [string.strip() for string in value.split(",")]


class Word(BaseTable):
    """Table for text tasks."""

    __tablename__ = "words"

    word: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(64), unique=True)
    description: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(1024))
    synonyms: orm.Mapped[str] = orm.mapped_column(CommaSeparatedList)
    antonyms: orm.Mapped[str] = orm.mapped_column(CommaSeparatedList)
    jeopardy: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(1024))
    s3_key: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(1024), unique=True)
