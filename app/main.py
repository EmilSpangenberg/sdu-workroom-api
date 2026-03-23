from fastapi import FastAPI

from app.routers import (
    bookings_router,
    buildings_router,
    rooms_router,
    sensors_router,
    students_router,
)

app = FastAPI(
    title="SDU Workroom Finder API",
    description="Find ledige grupperum på SDU campus",
    version="1.0.0"
)


@app.get("/")
def home():
    return {"status": "online", "message": "SDU Workroom Finder API kører!"}


app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(sensors_router)
app.include_router(buildings_router)
app.include_router(students_router)
