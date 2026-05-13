import uuid
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventsModel, SyncMetadataModel


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: uuid.UUID):
        query = select(EventsModel).where(EventsModel.id == event_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def upsert(self, event_data: dict):
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

    async def get_last_metadata(self):
        query = select(SyncMetadataModel).order_by(
            SyncMetadataModel.last_sync_time.desc().limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_log(self, status: str, last_changed_at):
        new_log = SyncMetadataModel(status=status, last_changed_at=last_changed_at)
        self.session.add(new_log)
        await self.session.commit()
