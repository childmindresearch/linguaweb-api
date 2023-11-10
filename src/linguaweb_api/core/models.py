"""Basic settings for all SQL tables."""
import datetime

import sqlalchemy
from sqlalchemy import orm

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
