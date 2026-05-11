import pytest
from unittest.mock import AsyncMock, patch
from app.client import EventProviderClient

@pytest.mark.asyncio
async def test_client_get_events_success():
    # Мокаем AsyncClient внутри httpx
    with patch("httpx.AsyncClient.get") as mock_get:
        # Настраиваем фейковый ответ от сервера
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"results": [{"id": "ev-1"}], "next": "cursor-2"}
        )

        client = EventProviderClient(base_url="http://api.test", api_key="token")
        response = await client.get_events(cursor="cursor-1")

        # Проверяем, что запрос ушел на правильный URL
        assert response.items[0]["id"] == "ev-1"
        assert response.next_cursor == "cursor-2"
        mock_get.assert_called_once()