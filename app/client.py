import uuid
from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel

from app.schemas import ProviderResponse


class EventProviderClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"x-api-key": f"{api_key}"}

    async def get_events(self, cursor: str) -> ProviderResponse:
        url = f"{self.base_url}/api/events/"
        params = {}
        if cursor:
            params["changed_at"] = str(cursor)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params={"changed_at": cursor},
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()

            return ProviderResponse(
                item=data.get("results", []),
                next_cursor=data.get("next")
            )

    async def get_event_seats(self, event_id: uuid.UUID):
        url = f"{self.base_url}/api/events/{event_id}/seats/"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code != 200:
                return []
            return response.json()


class EventPaginator:
    def __init__(self, client: EventProviderClient, start_cursor: str):
        self.client = client
        self.cursor = start_cursor
        self.buffer = []
        self.is_exhausted = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.buffer and not self.is_exhausted:
            response = await self.client.get_events(self.cursor)
            self.buffer = response.results
            self.cursor = response.next_cursor
            if not self.cursor:
                self.is_exhausted = True

        if not self.buffer:
            raise StopAsyncIteration

        return self.buffer.pop(0)
