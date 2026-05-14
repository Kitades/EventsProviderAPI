import uuid
import fastapi
from fastapi import APIRouter, BackgroundTasks, Depends

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

router = APIRouter(prefix="/api", tags=["Работа с API"])


@router.post("/sync/trigger")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    usecase: SyncEventUsecase = Depends(get_sync_usecase),
):
    background_tasks.add_task(usecase.execute)
    return {"status": "sync task"}


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/tickets")
async def create_ticket(
    event_id: str,
    first_name: str,
    last_name: str,
    seat: str,
    usecase: CreateTicketUsecase = Depends(get_ticket_usecase),
):
    ticket_id = await usecase.execute(event_id, first_name, last_name, seat)
    return {"ticket_id": ticket_id}


@router.get("/events/{event_id}", response_model=EventResponseSchema)
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


@router.get("events/{event_id}/seats", response_model=EventSeatsResponse)
async def get_seats(
    event_id: uuid.UUID, client: EventProviderClient = Depends(get_event_client)
):
    external_seats = await client.get_event_seats(event_id)
    return {"event_id": event_id, "available_seats": external_seats}
