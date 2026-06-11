from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import router
from app.database import engine
from app.models import Base
import asyncio
from app.usecases import SyncEventUsecase
from app.dependencies import get_sync_usecase


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        pass


app = FastAPI(title="Events Aggregator", lifespan=lifespan)


async def periodic_sync():
    while True:
        await asyncio.sleep(86400)
        usecase = get_sync_usecase(...)  # нужна зависимость
        await usecase.execute()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    task = asyncio.create_task(periodic_sync())
    yield
    task.cancel()


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
