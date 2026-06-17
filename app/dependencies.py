from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.client import EventProviderClient
from app.config import settings
from app.database import get_db
from app.repositories import EventRepository, SyncRepositories, TicketRepository
from app.usecases import (
    SyncEventUsecase,
    CreateTicketUsecase,
    CancelTicketUsecase,
    GetEventsUsecase,
    GetEventDetailUsecase,
    GetSeatsUsecase
)


def get_event_client():
    return EventProviderClient(
        base_url=settings.get_provider_url(), api_key=settings.get_return_api_key()
    )


def get_event_repository(db: AsyncSession = Depends(get_db)):
    return EventRepository(db)


def get_sync_usecase(
        event_repo: EventRepository = Depends(get_event_repository),
        db: AsyncSession = Depends(get_db),
        client: EventProviderClient = Depends(get_event_client),
):
    sync_repo = SyncRepositories(db)
    return SyncEventUsecase(client, event_repo, sync_repo)


def get_ticket_usecase(
        db: AsyncSession = Depends(get_db),
        client: EventProviderClient = Depends(get_event_client),
):
    event_repo = EventRepository(db)
    ticket_repo = TicketRepository(db)
    return CreateTicketUsecase(client, event_repo, ticket_repo)


def get_cancel_ticket_usecase(
        db: AsyncSession = Depends(get_db),
        client: EventProviderClient = Depends(get_event_client),
):
    ticket_repo = TicketRepository(db)
    return CancelTicketUsecase(client, ticket_repo)


def get_get_events_usecase(
        repo: EventRepository = Depends(get_event_repository),
):
    return GetEventsUsecase(repo)


def get_get_event_detail_usecase(
        repo: EventRepository = Depends(get_event_repository),
):
    return GetEventDetailUsecase(repo)


def get_get_seats_usecase(
        client: EventProviderClient = Depends(get_event_client),
):
    return GetSeatsUsecase(client)
