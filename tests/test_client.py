from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.client import EventProviderClient
from app.schemas import ProviderResponse


@pytest.mark.asyncio
async def test_get_events_with_changed_at():
    client = EventProviderClient(base_url='https://api.example.com', api_key='test')
    with patch('httpx.AsyncClient') as mock_httpx_client_class:
        # Создаём мок для ответа (синхронные методы)
        mock_response = Mock()
        mock_response.json = Mock(
            return_value={'results': [{'id': 1}], 'next': 'cursor'}
        )
        mock_response.raise_for_status = Mock()

        # Создаём мок для клиента (асинхронный)
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_httpx_client_class.return_value = mock_client

        response = await client.get_events(url=None, changed_at='2020-01-01')
        assert response == ProviderResponse(results=[{'id': 1}], next_cursor='cursor')
        mock_client.get.assert_awaited_with(
            'https://api.example.com/api/events/',
            params={'changed_at': '2020-01-01'},
            headers={'x-api-key': 'test'},
        )


@pytest.mark.asyncio
async def test_get_events_with_url():
    client = EventProviderClient(base_url='https://api.example.com', api_key='test')
    with patch('httpx.AsyncClient') as mock_httpx_client_class:
        mock_response = Mock()
        mock_response.json = Mock(return_value={'results': [], 'next': None})
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_httpx_client_class.return_value = mock_client

        response = await client.get_events(
            url='https://api.example.com/api/events/?cursor=abc', changed_at=None
        )
        assert response == ProviderResponse(results=[], next_cursor=None)
        mock_client.get.assert_awaited_with(
            'https://api.example.com/api/events/?cursor=abc',
            params=None,
            headers={'x-api-key': 'test'},
        )
