from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import BookingCreate, BookingNearestCreate, BookingResponse
from app.services import BookingService

router = APIRouter()


@router.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    """
    Opret booking med concurrent access kontrol.
    Bruger SELECT ... FOR UPDATE til at låse rækken.
    """
    return BookingService(db).create_booking(booking)


@router.post("/bookings/nearest-auto", response_model=BookingResponse)
def create_booking_nearest(booking_nearest: BookingNearestCreate, db: Session = Depends(get_db)):
    """
    Auto-book the nearest available room based on device GPS coordinates.
    Finds the closest available room and creates a booking in one request.

    Request Body:
    - student_id: Student ID
    - device_latitude: Device's current latitude
    - device_longitude: Device's current longitude
    - start_time: Booking start time
    - end_time: Booking end time
    - min_capacity: Minimum room capacity (default: 1)
    - max_distance_km: Maximum search radius (default: 10 km)

    Returns: Created booking with the nearest available room
    """
    return BookingService(db).create_nearest_booking(booking_nearest)

@router.get("/bookings", response_model=list[BookingResponse])
def get_bookings(room_id: Optional[int] = None, db: Session = Depends(get_db)):
    return BookingService(db).get_bookings(room_id)


@router.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    return BookingService(db).cancel_booking(booking_id)
