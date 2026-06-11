import typing
import uuid
from datetime import datetime


class EventRepositoryProtocol(typing.Protocol):
    async def get_by_id(self, event_id: uuid.UUID) -> typing.Any: ...

    async def get_all(
            self, data_from: typing.Optional[datetime], limit: int, offset: int
    ) -> typing.Tuple[int, list]: ...

    async def upsert(self, date: dict) -> None: ...


class EventsProviderClientProtocol(typing.Protocol):
    async def events(self, cursor) -> typing.Any: ...

    async def register(
            self, event_id: uuid.UUID, first_name: str, last_name: str, email: str, seat: str
    ) -> str: ...

    async def cancel_registration(self, ticket_id: str) -> bool: ...


class SyncRepositoryProtocol(typing.Protocol):
    async def get_last_cursor(self) -> str: ...

    async def update_sync_info(
            self, last_changed_at: datetime, status: str
    ) -> None: ...
