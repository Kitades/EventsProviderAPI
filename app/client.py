from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel


class ProviderResponse(BaseModel):
    item: List[Dict[str, Any]]
    next_cursor: Optional[str]


class EventProviderClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"{api_key}"}

    async def get_events(self, cursor: str) -> ProviderResponse:
        async with httpx.AsyncClient() as client:
            response = client.get(f"{self.base_url}/events",
                                  params={"changed_at": cursor},
                                  headers=self.headers
                                  )
            data = response.json()
            return ProviderResponse(item=data["results"], next_cursor=data.get("next"))


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
            self.buffer = response.items
            self.cursor = response.next_cursor
            if not self.cursor:
                self.is_exhausted = True

        if not self.buffer:
            raise StopAsyncIteration

        return self.buffer.pop(0)
