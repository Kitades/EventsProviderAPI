from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, BackgroundTasks, Depends

from app.dependencies import get_sync_usecase, get_ticket_usecase
from app.usecases import SyncEventUsecase, CreateTicketUsecase

router = APIRouter(prefix="/api", tags=["Работа с API"])


@router.post("/sync")
async def trigger_sync(
        background_tasks: BackgroundTasks,
        usecase: SyncEventUsecase = Depends(get_sync_usecase)
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
        usecase: CreateTicketUsecase = Depends(get_ticket_usecase)
):
    ticket_id = await usecase.execute(event_id, first_name, last_name, seat)
    return {"ticket_id": ticket_id}
