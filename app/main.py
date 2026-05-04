"""
АЛГОРИТМ: Основной процесс агрегации
1. ПОДКЛЮЧИТЬСЯ к Events Provider API
2. ЗАПРОСИТЬ список всех событий за текущую неделю
3. ЕСЛИ API ответил успешно:
    - ДЛЯ КАЖДОГО события в списке:
        - ПРОВЕРИТЬ, нет ли этого события в нашей базе
        - ЕСЛИ событие новое:
            - ДОПОЛНИТЬ данные (например, добавить категорию)
            - СОХРАНИТЬ в нашу БД
4. ИНАЧЕ:
    - ЗАПИСАТЬ ошибку в лог
"""
from fastapi import FastAPI

EXTERNAL_API_URL = "https://events-provider.com/api"
SYNC_INTERVAL = 24*60*60
SEATS_CACHE_TTL = 30
INITIAL_SYNC_DATE = "2000-01-01"

app = FastAPI()
app.include_router()

if __name__ == "__main__":
    pass
