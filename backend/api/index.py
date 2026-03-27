"""
Vercel Serverless Entry Point
This file adapts the FastAPI app for Vercel's serverless environment.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

# Vercel expects a variable named 'app' or a handler
handler = app
