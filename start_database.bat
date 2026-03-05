@echo off
echo ================================
echo SDU Workroom Finder
echo Starting PostgreSQL in Docker...
echo ================================
echo.
docker-compose up -d
echo.
echo Database is starting...
timeout /t 5 /nobreak > nul
echo.
echo ================================
echo PostgreSQL is running!
echo ================================
echo.
echo Connection details:
echo   Host: localhost
echo   Port: 5432
echo   Database: sdu_workrooms
echo   Username: postgres
echo   Password: postgres123
echo.
echo To stop: run stop_database.bat
echo.
pause
