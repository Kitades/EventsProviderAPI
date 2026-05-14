from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Попробуй ПОКА НЕ ВКЛЮЧАТЬ остальное, чтобы проверить, пройдет ли Health Check
# app.include_router(router)
