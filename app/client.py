import uuid

import httpx

from app.schemas import ProviderResponse


class EventProviderClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"x-api-key": f"{api_key}"}

    async def get_events(
            self,
            url: str | None = None,
            changed_at: str | None = None,
    ) -> ProviderResponse:
        if url is None:
            url = f"{self.base_url}/api/events/"
            params = {"changed_at": changed_at}
        else:
            params = None

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()

            return ProviderResponse(
                results=data.get("results", []),
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
    def __init__(self, client: EventProviderClient, changed_at):
        self.client = client
        self.next_url = None
        self.changed_at = changed_at
        self.buffer = []
        self.is_exhausted = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        while not self.buffer and not self.is_exhausted:
            response = await self.client.get_events(
                url=self.next_url,
                changed_at=self.changed_at,
            )
            self.buffer.extend(response.results)
            self.next_url = response.next_cursor
            if not self.next_url:
                self.is_exhausted = True

        if not self.buffer:
            raise StopAsyncIteration

        return self.buffer.pop(0)
