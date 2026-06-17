import pytest
from unittest.mock import AsyncMock, patch
from app.client import EventProviderClient


@pytest.mark.asyncio
async def test_get_events_with_changed_at():
    client = EventProviderClient(base_url="https://api.example.com", api_key="test")
    with patch("httpx.AsyncClient") as mock_httpx:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"results": [], "next": None}
        mock_response.raise_for_status = AsyncMock()
        mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        response = await client.get_events(url=None, changed_at="2020-01-01")
        assert response.results == []
        assert response.next_cursor is None
        mock_httpx.return_value.__aenter__.return_value.get.assert_awaited_with(
            "https://api.example.com/api/events/",
            params={"changed_at": "2020-01-01"},
            headers={"x-api-key": "test"},
        )


@pytest.mark.asyncio
async def test_get_events_with_url():
    client = EventProviderClient(base_url="https://api.example.com", api_key="test")
    with patch("httpx.AsyncClient") as mock_httpx:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"results": [], "next": None}
        mock_response.raise_for_status = AsyncMock()
        mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        response = await client.get_events(
            url="https://api.example.com/api/events/?cursor=abc", changed_at=None
        )
        assert response.results == []
        mock_httpx.return_value.__aenter__.return_value.get.assert_awaited_with(
            "https://api.example.com/api/events/?cursor=abc",
            params=None,
            headers={"x-api-key": "test"},
        )
