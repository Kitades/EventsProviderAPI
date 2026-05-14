from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
import uuid


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
    visitors_count: int
    status: str
    place: PlaceSchema

    model_config = ConfigDict(from_attributes=True)


class SeatSchema(BaseModel):
    id: uuid.UUID
    row: str
    number: int
    price: int = Field(alias="cost")
    is_available: bool


class EventSeatsResponse(BaseModel):
    event_id: uuid.UUID
    available_seats: list[SeatSchema]
