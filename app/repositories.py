import uuid
from datetime import datetime, UTC
from typing import Tuple, Optional

from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventsModel, SyncMetadataModel


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: uuid.UUID):
        query = select(EventsModel).where(EventsModel.id == event_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
            self, data_from: Optional[datetime], limit: int, offset: int
    ) -> Tuple[int, list]:

        query = select(EventsModel)

        if data_from:
            query = query.where(EventsModel.event_time >= data_from)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar_one()

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        events = result.scalars().all()

        return total_count, list(events)

    async def upsert(self, event_data: dict):
        data = event_data.copy()
        place = data.pop("place", None)
        if place and isinstance(place, dict):
            data["place_id"] = uuid.UUID(
                place.get("id") if isinstance(place.get("id"), str) else place.get("id")
            )
            data["place_name"] = place.get("name")
            data["city"] = place.get("city")
            data["address"] = place.get("address")
            data["seats_pattern"] = place.get("seats_pattern")
        if "number_of_visitors" in data:
            data["visitors_count"] = data.pop("number_of_visitors")
            data.pop("changed_at", None)

        event = await self.get_by_id(event_data["id"])
        if event:
            for key, value in event_data.items():
                setattr(event, key, value)

        else:
            new_event = EventsModel(**event_data)
            self.session.add(new_event)

        await self.session.commit()


class SyncRepositories:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_sync_info(self, last_changed_at, status):
        if isinstance(last_changed_at, str):
            try:
                last_changed_at = datetime.fromisoformat(
                    last_changed_at.replace("Z", "+00:00")
                )
            except ValueError:
                last_changed_at = datetime.strptime(
                    last_changed_at, "%Y-%m-%d"
                ).replace(tzinfo=UTC)

        sync_log = SyncMetadataModel(
            last_sync_time=datetime.now(UTC),
            last_changed_at=last_changed_at,
            status=status
        )
        self.session.add(sync_log)
        await self.session.commit()

    async def get_last_metadata(self):
        query = (
            select(SyncMetadataModel)
            .order_by(SyncMetadataModel.last_sync_time.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_last_cursor(self):
        meta = await self.get_last_metadata()
        if not meta or not meta.last_changed_at:
            return None
        return meta.last_changed_at.strftime("%Y-%m-%d")

    async def create_log(self, status: str, last_changed_at):
        new_log = SyncMetadataModel(
            id=uuid.uuid4(),
            status=status,
            last_changed_at=last_changed_at
        )
        self.session.add(new_log)
        await self.session.commit()
