import uuid
from datetime import datetime
from typing import Optional

from app.models import EventStatus
from app.protocols import (
    EventRepositoryProtocol,
    EventsProviderClientProtocol,
    SyncRepositoryProtocol,
)
from app.client import EventPaginator, EventProviderClient
from app.repositories import TicketRepository, EventRepository


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
            event_repo: EventRepositoryProtocol,
            ticket_repo: TicketRepository,
    ):
        self.client = client
        self.event_repo = event_repo
        self.ticket_repo = ticket_repo

    async def execute(
            self,
            event_id: uuid.UUID,
            first_name: str,
            last_name: str,
            email: str,
            seat: str,
    ):
        event = await self.event_repo.get_by_id(event_id)
        if not event or event.status != EventStatus.published:
            raise Exception("Cобытие не найдено")

        ticket_id = await self.client.register(
            event_id, first_name, last_name, email, seat
        )
        await self.ticket_repo.create(
            uuid.UUID(ticket_id), event_id, first_name, last_name, email, seat
        )
        return ticket_id


class CancelTicketUsecase:
    def __init__(
            self, client: EventsProviderClientProtocol, ticket_repo: TicketRepository
    ):
        self.client = client
        self.ticket_repo = ticket_repo

    async def execute(self, ticket_id: str) -> bool:
        ticket = await self.ticket_repo.get(uuid.UUID(ticket_id))
        if not ticket:
            return False
        success = await self.client.cancel_registration(ticket.event_id, ticket_id)
        if success:
            await self.ticket_repo.delete(ticket.id)
        return success


class GetEventsUsecase:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    async def execute(self, page: int, page_size: int, date_from: Optional[datetime] = None):
        limit = page_size
        offset = (page - 1) * page_size
        total_count, events = await self.event_repo.get_all(
            date_from=date_from, limit=limit, offset=offset
        )

        base_url = "/api/events"
        next_page = f"{base_url}?page={page + 1}&page_size={page_size}"
        if date_from:
            next_page += f"&date_from={date_from.isoformat()}"
        prev_page = (
            f"{base_url}?page={page - 1}&page_size={page_size}" if page > 1 else None
        )
        if date_from and prev_page:
            prev_page += f"&date_from={date_from.isoformat()}"

        return {
            "count": total_count,
            "next": next_page if offset + limit < total_count else None,
            "previous": prev_page,
            "results": events,
        }


class GetEventDetailUsecase:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    async def execute(self, event_id: uuid.UUID):
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            return None
        return event


class GetSeatsUsecase:
    def __init__(self, client: EventProviderClient):
        self.client = client

    async def execute(self, event_id: uuid.UUID):
        seats = await self.client.get_event_seats(event_id)
        return seats
