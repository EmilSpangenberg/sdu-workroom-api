from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import BookingNearestCreate, BookingResponse
from app.services import BookingService

router = APIRouter()


@router.post("/bookings/nearest-auto", response_model=BookingResponse)
def create_booking_nearest(booking_nearest: BookingNearestCreate, db: Session = Depends(get_db)):
    """
    Auto-book the nearest available room based on gadget GPS coordinates.
    Finds the closest available room and creates a booking in one request.

    Request Body:
    - gadget_id: Gadget ID
    - gadget_latitude: Gadget's current latitude
    - gadget_longitude: Gadget's current longitude
    - booking_time: Booking duration in minutes
    - min_capacity: Minimum room capacity (default: 1)

    Returns: Created booking with the nearest available room
    """
    return BookingService(db).create_nearest_booking(booking_nearest)

@router.get("/bookings", response_model=list[BookingResponse])
def get_bookings(room_id: Optional[int] = None, db: Session = Depends(get_db)):
    return BookingService(db).get_bookings(room_id)


@router.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    return BookingService(db).cancel_booking(booking_id)
