"""
ФУНКЦИЯ run_sync_process():
    1. ЛОГИРОВАТЬ: "Начало синхронизации"
    2. ПОЛУЧИТЬ дату последней правки из SyncMetadata
    3. ЕСЛИ даты нет:
           start_date = INITIAL_SYNC_DATE
       ИНАЧЕ:
           start_date = Metadata.last_changed_at

    4. ПОПЫТАТЬСЯ:
        - events_list = ProviderClient.get_events(start_date)
        - ДЛЯ КАЖДОГО event В events_list:
            - ЕСЛИ event уже есть в БД:
                ОБНОВИТЬ данные (имя, время, места)
            - ИНАЧЕ:
                СОЗДАТЬ новую запись в БД
        - ОБНОВИТЬ SyncMetadata:
            status = "success",
            last_sync_time = СЕЙЧАС,
            last_changed_at = МАКС(event.changed_at)
    5. ПРИ ОШИБКЕ:
        - ЛОГИРОВАТЬ: "Ошибка: {текст}"
        - ОБНОВИТЬ SyncMetadata: status = "failed"
"""
from sqlalchemy.ext.asyncio import AsyncSession


async def run_sync(db: AsyncSession):
    client =
