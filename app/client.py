import time
import uuid
import httpx
from typing import Optional, List, Dict

from app.schemas import ProviderResponse


class EventProviderClient:
    _seats_cache: Dict[str, tuple[float, List[str]]] = {}

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"x-api-key": api_key}

    async def get_events(
        self, url: Optional[str] = None, changed_at: Optional[str] = None
    ) -> ProviderResponse:
        if url is None:
            url = f"{self.base_url}/api/events/"
            params = {"changed_at": changed_at} if changed_at else None
        else:
            params = None

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return ProviderResponse(
                results=data.get("results", []),
                next_cursor=data.get("next")
            )

    async def get_event_seats(self, event_id: uuid.UUID) -> List[str]:
        cache_key = str(event_id)
        now = time.time()
        if cache_key in self._seats_cache:
            timestamp, seats = self._seats_cache
            if now - timestamp < 30:
                return seats

        url = f"{self.base_url}/api/events/{event_id}/seats/"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("seats") or data.get("available_seats") or data.get("results") or []
            else:
                items = []
            seats = []
            for item in items:
                if isinstance(item, dict):
                    seat_id = item.get("id") or item.get("seat") or str(item)
                    seats.append(seat_id)
                else:
                    seats.append(str(item))

            self._seats_cache[cache_key] = (now, seats)
            return seats

    async def register(
        self,
        event_id: uuid.UUID,
        first_name: str,
        last_name: str,
        email: str,
        seat: str
    ) -> str:
        url = f"{self.base_url}/api/events/{event_id}/tickets/"
        payload = {
            # "event_id": str(event_id),
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data["ticket_id"]

    async def cancel_registration(self, ticket_id: str) -> bool:
        url = f"{self.base_url}/api/tickets/{ticket_id}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers)
            response.raise_for_status()
            return True


class EventPaginator:
    def __init__(self, client: EventProviderClient, start_cursor: str):
        self.client = client
        self.next_url = None
        self.changed_at = start_cursor
        self.buffer = []
        self.is_exhausted = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        while not self.buffer and not self.is_exhausted:
            if self.next_url is None:
                response = await self.client.get_events(url=None, changed_at=self.changed_at)
            else:
                response = await self.client.get_events(url=self.next_url, changed_at=None)
            self.buffer.extend(response.results)
            self.next_url = response.next_cursor
            if not self.next_url:
                self.is_exhausted = True
        if not self.buffer:
            raise StopAsyncIteration
        return self.buffer.pop(0)