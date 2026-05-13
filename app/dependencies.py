from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.client import EventProviderClient
from app.database import get_db
from app.repositories import EventRepository, SyncRepositories
from app.usecases import SyncEventUsecase, CreateTicketUsecase


def get_event_client():
    return EventProviderClient(base_url="https://api.provider.com", api_key="secret")


def get_sync_usecase(
    db: AsyncSession = Depends(get_db),
    client: EventProviderClient = Depends(get_event_client),
):
    event_repo = EventRepository(db)
    sync_repo = SyncRepositories(db)
    return SyncEventUsecase(client, event_repo, sync_repo)


def get_ticket_usecase(
    db: AsyncSession = Depends(get_db),
    client: EventProviderClient = Depends(get_event_client),
):
    event_repo = EventRepository(db)
    return CreateTicketUsecase(client, event_repo)
