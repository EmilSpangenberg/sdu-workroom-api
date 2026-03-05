# Docker Setup Guide

## Filer i denne mappe

| Fil | Beskrivelse |
|-----|-------------|
| `docker-compose.yml` | Definerer PostgreSQL containeren |
| `schema.sql` | Database tabeller (køres automatisk) |
| `start_database.bat` | Start databasen |
| `stop_database.bat` | Stop databasen |
| `main.py` | API'en |
| `run_api.bat` | Start API'en |

---

## Første gang setup

### 1. Installer Docker Desktop
- Download fra https://www.docker.com/products/docker-desktop/
- Installer og genstart computeren
- Åbn Docker Desktop og vent til den kører

### 2. Installer Python pakker
```
pip install -r requirements.txt
```

---

## Daglig brug

### Start alt
1. Dobbeltklik `start_database.bat` (starter PostgreSQL)
2. Dobbeltklik `run_api.bat` (starter API)
3. Åbn http://localhost:8000/docs

### Stop alt
1. Luk API vinduet (tryk Y for at stoppe)
2. Dobbeltklik `stop_database.bat`

---

## Kommandoer (hvis du foretrækker terminal)

```bash
# Start database
docker-compose up -d

# Se logs
docker-compose logs -f

# Stop database
docker-compose down

# Stop og slet alt data
docker-compose down -v
```

---

## Fordele ved denne setup

✅ Ingen PostgreSQL installation på Windows
✅ Nemt at dele med gruppemedlemmer
✅ Samme setup på alle computere
✅ Data gemmes mellem genstarter
✅ Nemt at slette og starte forfra
