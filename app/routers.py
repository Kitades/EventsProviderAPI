import uuid
import fastapi
from fastapi import APIRouter, Depends

from app.client import EventProviderClient
from app.dependencies import (
    get_sync_usecase,
    get_ticket_usecase,
    get_event_repository,
    get_event_client,
)
from app.repositories import EventRepository
from app.schemas import EventResponseSchema, EventSeatsResponse
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


@router.get("/api/events", response_model=list[EventResponseSchema])
async def get_events(repo: EventRepository = Depends(get_event_repository)):
    events = await repo.get_all()
    results = [
        {
            "id": e.id,
            "name": e.name,
            "event_time": e.event_time,
            "registration_deadline": e.registration_deadline,
            "status": e.status,
            "number_of_visitors": e.visitors_count,
            "place": {
                "id": e.place_id,
                "name": e.place_name,
                "city": e.city,
                "address": e.address,
                "seats_pattern": e.seats_pattern,
            },
        }
        for e in events
    ]
    return {"count": len(results), "next": None, "previous": None, "results": results}


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
        "visitors_count": event.visitors_count,
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
