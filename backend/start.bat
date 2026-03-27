@echo off
REM Population Density API - Windows Startup Script

echo Starting Population Density FastAPI Backend...
echo ==========================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\.installed" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo. > venv\.installed
)

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found. Copying from .env.example...
    copy .env.example .env
    echo Please edit .env file and add your API keys
)

REM Start the server
echo Starting server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo ==========================================
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
