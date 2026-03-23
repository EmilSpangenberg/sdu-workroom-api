from .buildings import router as buildings_router
from .bookings import router as bookings_router
from .rooms import router as rooms_router
from .sensors import router as sensors_router
from .students import router as students_router

__all__ = [
    "buildings_router",
    "bookings_router",
    "rooms_router",
    "sensors_router",
    "students_router",
]
