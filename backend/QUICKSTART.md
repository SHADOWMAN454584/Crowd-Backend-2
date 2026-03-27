# Quick Start Guide - Population Density API

## 🚀 Get Started in 5 Minutes

### Step 1: Navigate to Backend
```bash
cd backend
```

### Step 2: Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your keys (optional for basic testing)
# Minimum config for testing:
ALLOWED_ORIGINS=*
ENABLE_REALTIME_MAPS=false
```

### Step 4: Run the Server
```bash
uvicorn app.main:app --reload
```

OR use the startup script:
```bash
# Windows:
start.bat

# macOS/Linux:
./start.sh
```

### Step 5: Test the API

Open your browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Locations**: http://localhost:8000/locations

## 📡 API Examples

### Get All Locations
```bash
curl http://localhost:8000/locations
```

### Get Current Hour Predictions
```bash
curl http://localhost:8000/predictions/bulk
```

### Get Predictions for Specific Hour (e.g., 18:00)
```bash
curl http://localhost:8000/predictions/bulk?hour=18
```

### Get AI Insights (requires OpenAI API key)
```bash
curl -X POST http://localhost:8000/ai/insights \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Get Real-time Status
```bash
curl http://localhost:8000/realtime/status
```

## 🔑 API Keys (Optional)

### OpenAI (for AI features)
1. Sign up at https://platform.openai.com
2. Create API key
3. Add to .env: `OPENAI_API_KEY=sk-...`

### Google Maps (for real-time data)
1. Go to https://console.cloud.google.com
2. Enable Maps APIs
3. Create API key
4. Add to .env: `GOOGLE_MAPS_API_KEY=AIza...`

## 🧪 Testing Without API Keys

The backend works WITHOUT API keys! It will:
- ✅ Provide predictions based on time-of-day patterns
- ✅ Return location data
- ✅ Generate rule-based insights (fallback mode)
- ✅ Use OpenStreetMap for routing

API keys only enhance features with:
- 🤖 OpenAI: Better AI-generated insights
- 🗺️ Google Maps: Real-time traffic and place data

## 📱 Connect Frontend

Update Flutter app's API URL:
```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```

Or for deployed backend:
```bash
flutter run --dart-define=API_BASE_URL=https://your-backend-url.com
```

## 🐛 Troubleshooting

### Port 8000 already in use
```bash
# Use different port
uvicorn app.main:app --reload --port 8080
```

### Module import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### CORS errors from Flutter app
Add your frontend URL to .env:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 📚 Next Steps

1. Explore API docs at http://localhost:8000/docs
2. Add your API keys to .env for enhanced features
3. Deploy to Vercel/Heroku (see README.md)
4. Customize locations in `app/data/locations.py`

## 🎯 Production Deployment

See `README.md` for detailed deployment guides for:
- Vercel
- Heroku
- Docker
- AWS/GCP/Azure

Happy coding! 🎉
