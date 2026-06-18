from unittest.mock import AsyncMock

import pytest

from app.schemas import ProviderResponse
from app.usecases import SyncEventUsecase


@pytest.mark.asyncio
async def test_sync_execute_success():
    mock_client = AsyncMock()
    mock_client.get_events.return_value = ProviderResponse(
        results=[{'id': 1, 'changed_at': '2023-01-01'}], next_cursor=None
    )
    mock_event_repo = AsyncMock()
    mock_sync_repo = AsyncMock()
    mock_sync_repo.get_last_cursor.return_value = '2000-01-01'

    usecase = SyncEventUsecase(mock_client, mock_event_repo, mock_sync_repo)
    await usecase.execute()

    mock_client.get_events.assert_awaited_with(url=None, changed_at='2000-01-01')
    mock_event_repo.upsert.assert_awaited_once_with(
        {'id': 1, 'changed_at': '2023-01-01'}
    )
    mock_sync_repo.update_sync_info.assert_awaited_once_with('2023-01-01', 'success')


@pytest.mark.asyncio
async def test_sync_execute_error():
    mock_client = AsyncMock()
    mock_client.get_events.side_effect = Exception('API error')
    mock_sync_repo = AsyncMock()
    mock_sync_repo.get_last_cursor.return_value = '2000-01-01'
    mock_event_repo = AsyncMock()

    usecase = SyncEventUsecase(mock_client, mock_event_repo, mock_sync_repo)
    with pytest.raises(Exception, match='API error'):
        await usecase.execute()
    mock_sync_repo.update_sync_info.assert_awaited_once_with('2000-01-01', 'error')
