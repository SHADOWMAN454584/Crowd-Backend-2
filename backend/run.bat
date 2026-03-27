@echo off
REM CrowdSense AI - Windows Startup Script
REM This script sets up and runs the FastAPI backend on Windows

echo ================================================================
echo   🚀 CrowdSense AI Backend - Starting Up
echo ================================================================

REM Navigate to backend directory
cd /d "%~dp0"

REM Check if .env file exists
if not exist .env (
    echo ⚠️  No .env file found. Creating from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo ✅ Created .env file. Please add your API keys!
    ) else (
        echo ❌ No .env.example found. Please create .env manually.
        exit /b 1
    )
)

REM Check for virtual environment
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt

echo.
echo ================================================================
echo   ✨ Backend Ready!
echo ================================================================
echo   📍 Local:     http://localhost:8000
echo   📚 Docs:      http://localhost:8000/docs
echo   ❤️  Health:    http://localhost:8000/health
echo ================================================================
echo.

REM Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
