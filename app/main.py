from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import router
from app.database import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:

        pass


app = FastAPI(
    title="Events Aggregator",
    lifespan=lifespan
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
