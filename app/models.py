"""
ТАБЛИЦА Events:
    id: UUID (Уникальный ключ)
    name: Строка
    city: Строка
    address: Строка
    event_time: ДатаВремя
    registration_deadline: ДатаВремя
    status: Строка (published/cancelled)
    visitors_count: Число

ТАБЛИЦА SyncMetadata:
    last_sync_time: ДатаВремя
    last_changed_at: ДатаВремя
    status: Строка (success/error)
"""
import datetime
import enum
import uuid
from sqlalchemy import Text, Enum, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql.annotation import Annotated

pk_id = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]
timestamp = Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]


class EventStatus(enum.Enum):
    published = "published"
    cancelled = "cancelled"


class SyncStatus(enum.Enum):
    success = "success"
    error = "error"


class Base(DeclarativeBase):
    __abstract__ = True


class Events(Base):
    id: Mapped[pk_id]
    name: Mapped[str] = mapped_column(Text, nullable=False)

    place_id: Mapped[uuid.UUID]
    place_name: Mapped[str]
    city: Mapped[str]
    address: Mapped[str]

    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    visitors_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, native_enum=False),
        default=EventStatus.published
    )


class SyncMetadata(Base):
    id: Mapped[pk_id]
    last_sync_time: Mapped[timestamp]
    last_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[SyncStatus] = mapped_column(Enum(SyncStatus, native_enum=False))
