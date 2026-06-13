import uuid
from datetime import datetime
from typing import Optional

import fastapi
from fastapi import APIRouter, Depends, Query, HTTPException

from app.client import EventProviderClient
from app.dependencies import (
    get_sync_usecase,
    get_ticket_usecase,
    get_event_repository,
    get_event_client, get_cancel_ticket_usecase,
)
from app.repositories import EventRepository
from app.schemas import (
    EventResponseSchema,
    EventSeatsResponse,
    EventsListResponseSchema, TicketCreateRequest,
)
from app.usecases import SyncEventUsecase, CreateTicketUsecase, CancelTicketUsecase

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


@router.post("/api/tickets", status_code=201)
async def create_ticket(
        payload: TicketCreateRequest,
        usecase: CreateTicketUsecase = Depends(get_ticket_usecase),
):
    ticket_id = await usecase.execute(
        event_id=payload.event_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        seat=payload.seat,
    )
    return {"ticket_id": ticket_id}


@router.get("/api/events", response_model=EventsListResponseSchema)
async def get_events(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1),
        date_from: Optional[datetime] = None,
        repo: EventRepository = Depends(get_event_repository),
):
    limit = page_size
    offset = (page - 1) * page_size
    total_count, events = await repo.get_all(date_from=date_from, limit=limit, offset=offset)

    base_url = "/api/events"
    next_page = f"{base_url}?page={page + 1}&page_size={page_size}"
    if date_from:
        next_page += f"&date_from={date_from.isoformat()}"
    prev_page = f"{base_url}?page={page - 1}&page_size={page_size}" if page > 1 else None
    if date_from and prev_page:
        prev_page += f"&date_from={date_from.isoformat()}"

    return {
        "count": total_count,
        "next": next_page if offset + limit < total_count else None,
        "previous": prev_page,
        "results": events,
    }


@router.get("/api/events/{event_id}", response_model=EventResponseSchema)
async def get_event_detail(
        event_id: uuid.UUID,
        repo: EventRepository = Depends(get_event_repository)
):
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="бывает просто не нашли")
    return event


@router.get("/api/events/{event_id}/seats", response_model=EventSeatsResponse)
async def get_seats(
        event_id: uuid.UUID,
        client: EventProviderClient = Depends(get_event_client)
):
    seats = await client.get_event_seats(event_id)
    if seats is None:
        raise HTTPException(status_code=404, detail="бывает просто не нашли")
    return {"event_id": event_id, "available_seats": seats}


@router.delete("/api/tickets/{ticket_id}")
async def cancel_ticket(
        ticket_id: str,
        usecase: CancelTicketUsecase = Depends(get_cancel_ticket_usecase),
):
    success = await usecase.execute(ticket_id)
    return {"success": success}
