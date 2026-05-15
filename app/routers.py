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
from app.schemas import EventResponseSchema, EventSeatsResponse, EventsListResponseSchema
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
        "results": events
    }


@router.get("/api/events/{event_id}", response_model=EventResponseSchema)
async def get_event_detail(
    event_id: uuid.UUID, repo: EventRepository = Depends(get_event_repository)
):
    event = await repo.get_by_id(event_id)
    if not event:
        raise fastapi.HTTPException(status_code=404, detail="Event not found")
    return {
        "id": event.id,
        "name": event.name,
        "event_time": event.event_time,
        "registration_deadline": event.registration_deadline,
        "number_of_visitors": event.number_of_visitors,
        "status": event.status,
        "place": {
            "id": event.place_id,
            "name": event.place_name,
            "city": event.city,
            "address": event.address,
            "seats_pattern": event.seats_pattern,
        },
    }


@router.get("/api/events/{event_id}/seats", response_model=EventSeatsResponse)
async def get_seats(
    event_id: uuid.UUID, client: EventProviderClient = Depends(get_event_client)
):
    external_seats = await client.get_event_seats(event_id)
    return {"event_id": event_id, "available_seats": external_seats}
