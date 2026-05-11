import pytest
from unittest.mock import AsyncMock, MagicMock
from app.usecases import SyncEventUsecase


@pytest.mark.asyncio
async def test_sync_usecase_flow():
    # Мокаем все зависимости
    mock_client = AsyncMock()
    mock_event_repo = AsyncMock()
    mock_sync_repo = AsyncMock()

    # Настраиваем: последняя синхронизация была "2023-01-01"
    mock_sync_repo.get_last_cursor.return_value = "2023-01-01"

    # Имитируем ответ провайдера (одна страница)
    mock_client.get_events.return_value = MagicMock(
        items=[{"id": "event-99", "changed_at": "2023-05-05"}],
        next_cursor=None
    )

    usecase = SyncEventUsecase(mock_client, mock_event_repo, mock_sync_repo)
    await usecase.execute()

    # Проверяем:
    # 1. Репозиторий событий вызвал сохранение
    mock_event_repo.upsert.assert_called_once()
    # 2. Репозиторий синхронизации обновил метаданные на "успех"
    mock_sync_repo.update_sync_info.assert_called_with("2023-05-05", "success")