import pytest
from unittest.mock import AsyncMock, MagicMock
from app.client import EventPaginator, EventProviderClient
from app.schemas import ProviderResponse


@pytest.fixture
def mock_client():
    client = MagicMock(spec=EventProviderClient)
    client.get_events = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_paginator_first_page(mock_client):
    mock_client.get_events.return_value = ProviderResponse(
        results=[{"id": 1, "name": "Event 1"}],
        next_cursor="cursor_2"
    )

    paginator = EventPaginator(client=mock_client, start_cursor="2020-01-01")
    events = []
    async for event in paginator:
        events.append(event)

    assert len(events) == 1
    assert events[0]["id"] == 1
    mock_client.get_events.assert_awaited_once_with(
        url=None,
        changed_at="2020-01-01"
    )


@pytest.mark.asyncio
async def test_paginator_multiple_pages(mock_client):
    mock_client.get_events.side_effect = [
        ProviderResponse(results=[{"id": 1}], next_cursor="cursor_2"),
        ProviderResponse(results=[{"id": 2}], next_cursor=None),
    ]

    paginator = EventPaginator(client=mock_client, start_cursor="2020-01-01")
    events = []
    async for event in paginator:
        events.append(event)

    assert len(events) == 2
    calls = mock_client.get_events.await_args_list
    assert calls[0].kwargs == {"url": None, "changed_at": "2020-01-01"}
    assert calls[1].kwargs == {"url": "cursor_2", "changed_at": None}