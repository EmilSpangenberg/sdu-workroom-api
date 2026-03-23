from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Booking, RoomCondition, Workroom
from app.schemas import BookingCreate, BookingNearestCreate, BookingResponse
from app.utils import haversine_distance

router = APIRouter()


@router.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    """
    Opret booking med concurrent access kontrol.
    Bruger SELECT ... FOR UPDATE til at låse rækken.
    """
    try:
        room = db.query(Workroom).filter(Workroom.id == booking.room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Rum ikke fundet")

        existing_booking = db.query(Booking).filter(
            and_(
                Booking.room_id == booking.room_id,
                Booking.status == "confirmed",
                Booking.start_time < booking.end_time,
                Booking.end_time > booking.start_time
            )
        ).with_for_update().first()

        if existing_booking:
            raise HTTPException(
                status_code=409,
                detail="Rummet er allerede booket i dette tidsrum"
            )

        new_booking = Booking(
            room_id=booking.room_id,
            student_id=booking.student_id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            status="confirmed"
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

        return BookingResponse(
            id=new_booking.id,
            room_id=new_booking.room_id,
            student_id=new_booking.student_id,
            start_time=new_booking.start_time,
            end_time=new_booking.end_time,
            status=new_booking.status,
            latitude=room.latitude,
            longitude=room.longitude
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
        max_distance_meters = booking_nearest.max_distance_km * 1000
        nearest_room = None
        nearest_distance = float("inf")

        rooms = db.query(Workroom).filter(
            Workroom.capacity >= booking_nearest.min_capacity
        ).all()

        for room in rooms:
            condition = db.query(RoomCondition).filter(
                RoomCondition.room_id == room.id
            ).first()

            if condition and not condition.is_occupied:
                distance = haversine_distance(
                    booking_nearest.device_latitude,
                    booking_nearest.device_longitude,
                    room.latitude,
                    room.longitude
                )

                if distance <= max_distance_meters and distance < nearest_distance:
                    nearest_distance = distance
                    nearest_room = room

        if not nearest_room:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No available rooms found within {booking_nearest.max_distance_km} km "
                    f"with capacity {booking_nearest.min_capacity}+"
                )
            )

        existing_booking = db.query(Booking).filter(
            and_(
                Booking.room_id == nearest_room.id,
                Booking.status == "confirmed",
                Booking.start_time < booking_nearest.end_time,
                Booking.end_time > booking_nearest.start_time
            )
        ).with_for_update().first()

        if existing_booking:
            raise HTTPException(
                status_code=409,
                detail="Nearest room was just booked by another user. Try again to find next nearest room."
            )

        new_booking = Booking(
            room_id=nearest_room.id,
            student_id=booking_nearest.student_id,
            start_time=booking_nearest.start_time,
            end_time=booking_nearest.end_time,
            status="confirmed"
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

        return BookingResponse(
            id=new_booking.id,
            room_id=new_booking.room_id,
            student_id=new_booking.student_id,
            start_time=new_booking.start_time,
            end_time=new_booking.end_time,
            status=new_booking.status,
            latitude=nearest_room.latitude,
            longitude=nearest_room.longitude
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_bookings(room_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Booking)
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    return query.all()


@router.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking ikke fundet")

    booking.status = "cancelled"
    db.commit()
    return {"message": "Booking annulleret"}
