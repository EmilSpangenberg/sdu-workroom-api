# SDU Workroom Finder API

FastAPI backend for finding available study/work rooms and creating bookings.
The database is hosted on Supabase (PostgreSQL).

## Project structure

| File/Folder | Description |
| --- | --- |
| `app/` | Application package (routers, services, models, schemas, db config) |
| `main.py` | Compatibility launcher that starts the API app |
| `run_api.bat` | Windows shortcut script to run the API |
| `requirements.txt` | Python dependencies |
| `schema.sql` | SQL schema you can run in Supabase SQL Editor |

## Prerequisites

1. Python 3.10+ (3.13 also works with compatible package versions)
2. A Supabase project with PostgreSQL enabled

## Setup

### 1. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres
```

Get the connection string from Supabase:
`Project Settings -> Database -> Connection string`.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the API

### Option A (Windows script)

```bash
run_api.bat
```

### Option B (terminal)

```bash
python main.py
```

API docs will be available at:
[http://localhost:8000/docs](http://localhost:8000/docs)

## Run with Docker

### 1. Build image

```bash
docker build -t sdu-workroom-api .
```

### 2. Run container

```bash
docker run --rm -p 8000:8000 --env-file .env sdu-workroom-api
```

API docs will be available at:
[http://localhost:8000/docs](http://localhost:8000/docs)

### Optional: Run with Docker Compose

```bash
docker compose up --build
```

## ESP32-C6 integration (recommended)

Use local LAN first (same Wi-Fi as your API host), then harden security later.

### 1. Network setup

1. Run API on a machine in your LAN.
2. Use host binding `0.0.0.0` (already used in `main.py`).
3. Find the API machine LAN IP, for example `192.168.1.50`.
4. From ESP32, call `http://192.168.1.50:8000/...`.
5. Allow inbound port `8000` in your OS firewall.

### 2. Example endpoint calls

#### Nearest auto booking

`POST /bookings/nearest-auto`

```json
{
  "student_id": 1,
  "device_latitude": 55.35254,
  "device_longitude": 10.42624,
  "start_time": "2026-03-23T10:00:00",
  "end_time": "2026-03-23T11:00:00",
  "min_capacity": 1,
  "max_distance_km": 10.0
}
```

#### Sensor update

`POST /sensors/update?room_id=1&noise_level=42&temperature=22.5&is_occupied=true`

### 3. Embedded best practices

1. Set client timeout (for example 5 seconds).
2. Retry once on timeout or 5xx.
3. Do not auto-retry 409 conflicts; issue a new nearest-room request.
4. Parse only required response fields to reduce RAM usage.

## Notes

1. `DATABASE_URL` must be set correctly, or the app will fail at startup.
2. If dependency installation fails on Python 3.13 with old pinned versions, update packages to Python 3.13-compatible releases.


{
  "student_id": 1,
  "device_latitude": 55.35282,
  "device_longitude": 10.42801,
  "start_time": "2026-03-24T08:41:17.594Z",
  "end_time": "2026-03-24T08:41:17.594Z",
  "min_capacity": 5,
  "max_distance_km": 10
}


device sends
{
  "device_id": 1,
  "device_latitude": 55.35282,
  "device_longitude": 10.42801,
  "booking_time": int (minutes),
  "min_capacity": 5,
}

