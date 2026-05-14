from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import router
from app.database import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте приложения создаем таблицы, если их нет
    async with engine.begin() as conn:
        # Это поможет избежать 503 из-за отсутствия колонок
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        # Тут можно закрывать соединения, если нужно
        pass


app = FastAPI(title="Events Aggregator", lifespan=lifespan)


# Прямой Health Check (тест просит именно /api/health)
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# Подключаем остальные роутеры
app.include_router(router)

# Запуск для локальной отладки (на LMS не мешает)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
