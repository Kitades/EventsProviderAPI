import uuid

from .protocols import (
    EventRepositoryProtocol,
    EventsProviderClientProtocol,
    SyncRepositoryProtocol,
)
from .client import EventPaginator


class SyncEventUsecase:
    def __init__(
        self,
        client: EventsProviderClientProtocol,
        event_repo: EventRepositoryProtocol,
        sync_repo: SyncRepositoryProtocol,
    ):
        self.client = client
        self.event_repo = event_repo
        self.sync_repo = sync_repo

    async def execute(self):
        cursor = await self.sync_repo.get_last_cursor() or "2000-01-01"
        paginator = EventPaginator(self.client, start_cursor=cursor)
        last_event_date = cursor
        try:
            async for event_data in paginator:
                await self.event_repo.upsert(event_data)
                last_event_date = event_data.get("changed_at", last_event_date)

            await self.sync_repo.update_sync_info(last_event_date, "success")
        except Exception:
            await self.sync_repo.update_sync_info(last_event_date, "error")
            raise


class CreateTicketUsecase:
    def __init__(
        self,
        client: EventsProviderClientProtocol,
        event_repo: EventRepositoryProtocol
    ):
        self.client = client
        self.event_repo = event_repo

    async def execute(
        self,
        event_id: uuid.UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str
    ):
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            raise Exception("Cобытие не найдено")

        if event.status != "published":
            raise Exception("Регистрация не возможна: Событие не опубликованно")

        ticket_id = await self.client.register(
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat
        )
        return ticket_id


class CancelTicketUsecase:
    def __init__(self, client: EventsProviderClientProtocol):
        self.client = client

    async def execute(self, ticket_id: str) -> bool:
        return await self.client.cancel_registration(ticket_id)