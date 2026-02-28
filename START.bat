@echo off
REM RAG System - Windows Startup Script

echo.
echo ================================================
echo.
echo   🚀 RAG Semantic Search System - Windows Start
echo.
echo ================================================
echo.

REM Check if Docker is running
echo Checking PostgreSQL with pgvector...
docker ps 2>nul | findstr "postgres_vectordb" >nul
if errorlevel 1 (
    echo Starting PostgreSQL...
    cd docker
    docker-compose up -d
    cd ..
    echo ⏳ Waiting for PostgreSQL to be ready...
    timeout /t 10
) else (
    echo ✅ PostgreSQL is running
)

echo.
echo Installing/Verifying dependencies...
pip install -r requirements.txt -q

echo.
echo.
echo ================================================
echo Starting Services...
echo ================================================
echo.

REM Start Backend in a new window
echo 📍 BACKEND: http://127.0.0.1:8000
echo 📍 API DOCS: http://127.0.0.1:8000/docs
echo.
start cmd /k "cd %cd% && python app/main.py"

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start Frontend
echo.
echo Frontend starting...
echo 📍 FRONTEND: http://localhost:3000
echo.
cd frontend
npm run dev

pause
