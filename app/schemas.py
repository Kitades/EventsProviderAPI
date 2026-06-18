from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, model_validator

from app.models import EventStatus


class PlaceSchema(BaseModel):
    id: uuid.UUID
    name: str
    city: str
    address: str
    seats_pattern: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EventResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    event_time: datetime
    registration_deadline: datetime
    number_of_visitors: int
    status: EventStatus
    place: PlaceSchema

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def bundle_place_fields(cls, data):
        if hasattr(data, 'place_id'):
            return {
                'id': data.id,
                'name': data.name,
                'event_time': data.event_time,
                'registration_deadline': data.registration_deadline,
                'status': data.status,
                'number_of_visitors': getattr(
                    data, 'number_of_visitors', getattr(data, 'visitors_count', 0)
                ),
                'place': {
                    'id': data.place_id,
                    'name': data.place_name,
                    'city': data.city,
                    'address': data.address,
                    'seats_pattern': data.seats_pattern,
                },
            }
        return data


class ProviderResponse(BaseModel):
    results: list[dict[str, Any]]
    next_cursor: str | None


class EventsListResponseSchema(BaseModel):
    count: int
    next: str | None = None
    previous: str | None = None
    results: list[EventResponseSchema]


class TicketCreateRequest(BaseModel):
    event_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    seat: str


class EventSeatsResponse(BaseModel):
    event_id: uuid.UUID
    available_seats: list[str]
