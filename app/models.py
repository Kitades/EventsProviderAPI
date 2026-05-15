from datetime import datetime
import enum
import uuid
from typing import Annotated
from sqlalchemy import Text, Enum, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


pk_id = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]
timestamp = Annotated[
    datetime, mapped_column(DateTime(timezone=True), server_default=func.now())
]


class EventStatus(enum.Enum):
    published = "published"
    cancelled = "cancelled"


class SyncStatus(enum.Enum):
    success = "success"
    error = "error"


class Base(DeclarativeBase):
    __abstract__ = True


class EventsModel(Base):
    __tablename__ = "event"
    id: Mapped[pk_id]
    name: Mapped[str] = mapped_column(Text, nullable=False)

    place_id: Mapped[uuid.UUID]
    place_name: Mapped[str]
    city: Mapped[str]
    address: Mapped[str]
    seats_pattern: Mapped[str | None] = mapped_column(Text, nullable=True)

    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    number_of_visitors: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, native_enum=False), default=EventStatus.published
    )


class SyncMetadataModel(Base):
    __tablename__ = "sync"
    id: Mapped[pk_id]
    last_sync_time: Mapped[timestamp]
    last_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[SyncStatus] = mapped_column(Enum(SyncStatus, native_enum=False))
