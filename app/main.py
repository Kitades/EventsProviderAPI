import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from app.client import EventProviderClient
from app.config import settings
from app.database import AsyncSessionLocal, engine
from app.models import Base
from app.repositories import EventRepository, SyncRepositories
from app.routers import router
from app.usecases import SyncEventUsecase


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    task = asyncio.create_task(periodic_sync())
    yield
    task.cancel()
    await task


app = FastAPI(title='Events Aggregator', lifespan=lifespan)


async def periodic_sync():
    while True:
        await asyncio.sleep(86400)
        try:
            async with AsyncSessionLocal() as db:
                event_repo = EventRepository(db)
                sync_repo = SyncRepositories(db)
                client = EventProviderClient(
                    base_url=settings.get_provider_url(),
                    api_key=settings.get_return_api_key(),
                )
                usecase = SyncEventUsecase(client, event_repo, sync_repo)
                await usecase.execute()
        except Exception as e:
            print(f'Periodic sync error: {e}')


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exc.errors()},
    )


app.include_router(router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
