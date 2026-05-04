import httpx


class EventProviderClient:
    BASE_URL = "https://provider.api/v1"

    async def fetch_event(self, changed_at: str):
        async with httpx.AsyncClient() as client:
            response = client.get(f"{self.BASE_URL}/events", params={"changed_at": changed_at})
            return response.json()

    async def get_seats(self, event_id: str):

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/events/{event_id}/seats")
            return response.json()

