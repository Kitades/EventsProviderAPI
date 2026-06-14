from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import router
from app.database import engine
from app.models import Base
import asyncio
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    task = asyncio.create_task(periodic_sync())
    yield
    task.cancel()
    await task


app = FastAPI(title="Events Aggregator", lifespan=lifespan)


async def periodic_sync():
    """Фоновая синхронизация раз в 24 часа"""
    while True:
        await asyncio.sleep(86400)
        try:
            # from app.database import AsyncSessionLocal
            # async with AsyncSessionLocal() as db:
            #     event_repo = EventRepository(db)
            #     sync_repo = SyncRepositories(db)
            #     client = get_event_client()
            #     usecase = SyncEventUsecase(client, event_repo, sync_repo)
            #     await usecase.execute()
            pass
        except Exception as e:
            print(f"Periodic sync error: {e}")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
