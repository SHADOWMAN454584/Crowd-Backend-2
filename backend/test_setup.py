#!/usr/bin/env python
"""
Quick Test Script
Run this to verify backend is working correctly.
"""
import sys
import importlib.util

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    modules = ['fastapi', 'uvicorn', 'pydantic', 'googlemaps', 'openai']

    for module in modules:
        spec = importlib.util.find_spec(module)
        if spec is not None:
            print(f"  [OK] {module}")
        else:
            print(f"  [FAIL] {module} - NOT INSTALLED")
            return False
    return True

def test_config():
    """Test if configuration loads correctly."""
    print("\nTesting configuration...")
    try:
        from app.core.config import settings
        print(f"  [OK] Config loaded")
        print(f"  [OK] App Name: {settings.app_name}")
        print(f"  [OK] OpenAI configured: {settings.openai_configured}")
        print(f"  [OK] Google Maps configured: {settings.google_maps_configured}")
        return True
    except Exception as e:
        print(f"  [FAIL] Config error: {e}")
        return False

def test_app():
    """Test if FastAPI app can be created."""
    print("\nTesting FastAPI app...")
    try:
        from app.main import app
        print(f"  [OK] FastAPI app created")
        print(f"  [OK] Title: {app.title}")
        return True
    except Exception as e:
        print(f"  [FAIL] App error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CrowdSense AI Backend - System Test")
    print("=" * 60)

    results = []
    results.append(test_imports())
    results.append(test_config())
    results.append(test_app())

    print("\n" + "=" * 60)
    if all(results):
        print("[SUCCESS] ALL TESTS PASSED")
        print("You can now run: python -m uvicorn app.main:app --reload")
        sys.exit(0)
    else:
        print("[ERROR] SOME TESTS FAILED")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
