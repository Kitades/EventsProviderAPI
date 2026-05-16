import uuid
from datetime import datetime
from typing import Optional

import fastapi
from fastapi import APIRouter, Depends, Query

from app.client import EventProviderClient
from app.dependencies import (
    get_sync_usecase,
    get_ticket_usecase,
    get_event_repository,
    get_event_client,
)
from app.repositories import EventRepository
from app.schemas import (
    EventResponseSchema,
    EventSeatsResponse,
    EventsListResponseSchema,
)
from app.usecases import SyncEventUsecase, CreateTicketUsecase

router = APIRouter()


@router.post("/api/sync/trigger")
async def trigger_sync(
    usecase: SyncEventUsecase = Depends(get_sync_usecase),
):
    await usecase.execute()
    return {"status": "ok"}


@router.get("/api/health")
async def health_check():
    return {"status": "ok"}


@router.post("/api/tickets")
async def create_ticket(
    event_id: str,
    first_name: str,
    last_name: str,
    seat: str,
    usecase: CreateTicketUsecase = Depends(get_ticket_usecase),
):
    ticket_id = await usecase.execute(event_id, first_name, last_name, seat)
    return {"ticket_id": ticket_id}


@router.get("/api/events", response_model=EventsListResponseSchema)
async def get_events(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    data_from: Optional[datetime] = None,
    repo: EventRepository = Depends(get_event_repository)
):

    total_count, events = await repo.get_all(
        data_from=data_from,
        limit=limit,
        offset=offset
    )

    return {
        "count": total_count,
        "next": None,
        "previous": None,
        "results": events}


@router.get("/api/events/{event_id}", response_model=EventResponseSchema)
async def get_event_detail(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, alias="page_size"),
        date_from: Optional[datetime] = Query(None, alias="date_from"),
        repo: EventRepository = Depends(get_event_repository)
):
    limit = page_size
    offset = (page - 1) * page_size
    total_count, events = await repo.get_all(
        data_from=date_from,
        limit=limit,
        offset=offset
    )
    return {
        "count": total_count,
        "next": None,
        "previous": None,
        "results": events
    }


@router.get("/api/events/{event_id}/seats", response_model=EventSeatsResponse)
async def get_seats(
    event_id: uuid.UUID, client: EventProviderClient = Depends(get_event_client)
):
    external_seats = await client.get_event_seats(event_id)
    return {
        "event_id": event_id,
        "available_seats": external_seats
    }
