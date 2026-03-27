#!/bin/bash

# CrowdSense AI - One Command Startup Script
# This script sets up and runs the FastAPI backend

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════"
echo "  🚀 CrowdSense AI Backend - Starting Up"
echo "════════════════════════════════════════════════════════════"

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please add your API keys!"
    else
        echo "❌ No .env.example found. Please create .env manually."
        exit 1
    fi
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✨ Backend Ready!"
echo "════════════════════════════════════════════════════════════"
echo "  📍 Local:     http://localhost:8000"
echo "  📚 Docs:      http://localhost:8000/docs"
echo "  ❤️  Health:    http://localhost:8000/health"
echo "════════════════════════════════════════════════════════════"
echo ""

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
