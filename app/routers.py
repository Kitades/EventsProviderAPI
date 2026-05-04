"""
0. Health check
Endpoint: GET /api/health

1. Фоновая синхронизация событий
Требование: Реализовать фоновый процесс синхронизации событий с Events Provider API
Функциональность:
Периодическая синхронизация событий раз в день
Использование инкрементальной синхронизации через параметр changed_at
Хранение метаданных синхронизации (last_sync_time, last_changed_at, sync_status)
Обработка первой синхронизации (получение всех событий с changed_at=2000-01-01)
Обработка последующих синхронизаций (получение только измененных событий)
Обновление или добавление событий в локальную базу данных
Логирование процесса синхронизации и ошибок

2. Ручной запуск синхронизации
Endpoint: POST /api/sync/trigger HTTP 200
3. Получение списка событий
Endpoint: GET /api/events HTTP 200
Query параметры:
date_from (опционально) - события после указанной даты (формат: YYYY-MM-DD)
page (опционально) - номер страницы (по умолчанию 1)
page_size (опционально) - размер страницы (по умолчанию 20)
{
  "count": 150,
  "next": "http://{hostname}/api/events/?page=2",
  "previous": null,
  "results": [
    {
      "id": "event-uuid",
      "name": "Название мероприятия",
      "place": {
        "id": "place-uuid",
        "name": "Название площадки",
        "city": "Город",
        "address": "Адрес"
      },
      "event_time": "2026-01-11T17:00:00+03:00",
      "registration_deadline": "2026-01-10T17:00:00+03:00",
      "status": "published",
      "number_of_visitors": 5
    }
  ]
}
4. Получение деталей события
Endpoint: GET /api/events/{event_id} HTTP 200
{
  "id": "event-uuid",
  "name": "Название мероприятия",
  "place": {
    "id": "place-uuid",
    "name": "Название площадки",
    "city": "Город",
    "address": "Адрес",
    "seats_pattern": "A1-1000,B1-2000"
  },
  "event_time": "2026-01-11T17:00:00+03:00",
  "registration_deadline": "2026-01-10T17:00:00+03:00",
  "status": "published",
  "number_of_visitors": 5
}
5. Получение информации о местах
Endpoint: GET /api/events/{event_id}/seats HTTP 200
{
  "event_id": "event-uuid",
  "available_seats": ["A1", "A3", "A4", ...]
}
6. Регистрация на событие
Endpoint: POST /api/tickets HTTP 201
Request Body:
{
  "event_id": "event-uuid",
  "first_name": "Иван",
  "last_name": "Иванов",
  "email": "ivan@example.com",
  "seat": "A15"
}
Ответ:
{
  "ticket_id": "ticket-uuid",
}
7. Отмена регистрации
Endpoint: DELETE /api/tickets/{ticket_id} HTTP 200
{
  "success": true
}



# Группа: Общее
GET /api/health:
    ВЕРНУТЬ {"status": "ok"}

POST /api/sync/trigger:
    ЗАПУСТИТЬ run_sync_process() в фоне
    ВЕРНУТЬ 200 "Синхронизация запущена"

# Группа: События (Работа с локальной БД)
GET /api/events:
    ПРИНЯТЬ date_from, page, page_size
    query = SELECT FROM Events WHERE time >= date_from
    results = ПРИМЕНИТЬ пагинацию к query (LIMIT page_size OFFSET (page-1)*page_size)
    ВЕРНУТЬ {count, results, next_link, prev_link}

GET /api/events/{id}:
    event = SELECT FROM Events WHERE id = {id}
    ЕСЛИ нет: ВЕРНУТЬ 404
    ИНАЧЕ: ВЕРНУТЬ event

# Группа: Интерактив (Работа через кэш или прокси)
GET /api/events/{id}/seats:
    ЕСЛИ есть в кэше {id}_seats И время < 30 сек:
        ВЕРНУТЬ данные из кэша
    ИНАЧЕ:
        seats = ProviderClient.get_seats(id)
        СОХРАНИТЬ seats в кэш
        ВЕРНУТЬ seats

POST /api/tickets:
    ПРОВЕРИТЬ валидность email и ID события
    result = ProviderClient.register_ticket(request_body)
    ВЕРНУТЬ result.ticket_id (201)

DELETE /api/tickets/{id}:
    УДАЛИТЬ ЧЕРЕЗ ProviderClient.cancel_ticket(id)
    ВЕРНУТЬ {"success": true}
"""
from datetime import datetime
from http.client import HTTPResponse
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.main import app
from app.models import Events

router = APIRouter(prefix="/api", tags=["Работа с API"])


@router.get("/health")
def health_check():
    if HTTPResponse == 200:
        return {"health": "ok"}
    return "Error"


@router.get("/events")
async def get_events(date_form: datetime,
                     page: Optional[int] = 1,
                     page_size: Optional[int] = 20,
                     db: AsyncSession = Depends(get_db)):
    query = select(Events)
    if date_form:
        query = query.where(Events.event_time >= date_form)

    count_query = select(func.count()).select_from(query.subquery())
    total_count = (await db.execute(count_query)).scalar()

    offset = (page - 1) * page_size
    query = query.limit(page_size).offset(offset)

    result = await db.execute(query)
    events = result.scalars().all()

    base_url = "/api/events/"
    next_link = f"{base_url}?page={page + 1}&page_size={page_size}" if offset + page_size < total_count else None
    prev_link = f"{base_url}?page={page - 1}&page_size={page_size}" if page > 1 else None

    return {
        "count": total_count,
        "next": next_link,
        "previous": prev_link,
        "results": events
    }

@app.get("/events/{event_id}")
async def get_events_id(db: AsyncSession = Depends(get_db)):
    event = select(Events).where(Events.id == "{event_id}")
    if
