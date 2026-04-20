from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoomResponse(BaseModel):
    id: int
    room_number: str
    capacity: int
    building_code: str
    building_name: str
    is_occupied: bool
    noise_level: Optional[float]
    temperature: Optional[float]
    latitude: float
    longitude: float
    distance_meters: Optional[float] = None

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    room_id: int
    gadget_id: int
    start_time: datetime
    end_time: datetime


class BookingNearestCreate(BaseModel):
    """Auto-book the nearest available room based on gadget GPS coordinates"""
    gadget_id: int
    gadget_latitude: float
    gadget_longitude: float
    booking_time: int  # in minutes
    min_capacity: int = 1


class BookingResponse(BaseModel):
    id: int
    room_id: int
    gadget_id: int
    start_time: datetime
    end_time: datetime
    status: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    sdu_id: str
    name: str
