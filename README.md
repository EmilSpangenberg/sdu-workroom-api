# API Setup Guide (Supabase)

## Filer i denne mappe

| Fil | Beskrivelse |
| --- | --- |
| `docker-compose.yml` | Ikke i brug til database (Supabase bruges) |
| `schema.sql` | Database tabeller (kør manuelt i Supabase SQL editor) |
| `start_database.bat` | Info-script (ingen lokal database) |
| `stop_database.bat` | Info-script (ingen lokal database) |
| `main.py` | API'en |
| `run_api.bat` | Start API'en |

---

## Første gang setup

### 1. Opret .env med Supabase connection string

Tilføj en `.env` fil i projektmappen med:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres
```

Brug connection string fra dit Supabase projekt (Settings -> Database).

### 2. Installer Python pakker

```bash
pip install -r requirements.txt
```

---

## Daglig brug

### Start alt

1. Dobbeltklik `run_api.bat` (starter API)
2. Åbn [http://localhost:8000/docs](http://localhost:8000/docs)

### Stop alt

1. Luk API vinduet (tryk Y for at stoppe)

---

## Kommandoer (hvis du foretrækker terminal)

```bash
# Start API
python main.py
```

---

## Bemærk
Husk at `DATABASE_URL` skal være sat korrekt i `.env`
