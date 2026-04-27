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

https://habr.com/ru/articles/828328/
"""
from app.main import app


@app.get("/health")
def health_check():
    if HTTPResponse == 200:
        return {"health": "ok"}
    return "Error"


@app.get("/events")
async def get_events():
    pass

@app.get("/events/{event_id")
async def get_events_id():
    pass

