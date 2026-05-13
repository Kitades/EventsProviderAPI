import pytest
from unittest.mock import AsyncMock, MagicMock

from app.client import EventPaginator


@pytest.mark.asyncio
async def test_paginator_successful_iteration():
    mock_client = AsyncMock()

    mock_client.events.side_effect = [
        MagicMock(items=[{"id": 1}, {"id": 2}], next_cursor="page_2"),
        MagicMock(items=[{"id": 3}], next_cursor=None),
    ]

    paginator = EventPaginator(client=mock_client, start_cursor="page_1")

    collected_events = []
    async for event in paginator:
        collected_events.append(event)

    assert len(collected_events) == 3
    assert collected_events[0]["id"] == 1
    assert collected_events[2]["id"] == 3

    assert mock_client.events.call_count == 2

    mock_client.events.assert_called_with(cursor="page_2")
