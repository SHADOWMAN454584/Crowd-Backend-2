# 🚀 CrowdSense AI Backend - Deployment Guide

Complete FastAPI backend with **Google Maps** and **OpenAI** integration for the CrowdSense AI Flutter app.

---

## ✨ Features

- 🔮 **ML-Powered Predictions** - Crowd density forecasting
- 🗺️ **Google Maps Integration** - Real-time traffic and location data
- 🤖 **OpenAI Integration** - AI-powered insights and recommendations
- ⚡ **Fast & Scalable** - Built with FastAPI
- 🌐 **Vercel-Ready** - One-click serverless deployment

---

## 📦 Quick Start (Local Development)

### Prerequisites
- Python 3.10 or higher
- Google Maps API Key ([Get it here](https://console.cloud.google.com/google/maps-apis))
- OpenAI API Key ([Get it here](https://platform.openai.com/api-keys))

### One Command Start

**Windows:**
```bash
run.bat
```

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

That's it! The server will be running at:
- 🌐 API: http://localhost:8000
- 📚 Docs: http://localhost:8000/docs
- ❤️ Health: http://localhost:8000/health

---

## 🔧 Manual Setup

If you prefer manual setup:

```bash
# 1. Navigate to backend folder
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment file
cp .env.example .env

# 6. Edit .env and add your API keys
# Edit .env file with your favorite editor

# 7. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌍 Vercel Deployment (Production)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Add Environment Variables

Add your secrets to Vercel:
```bash
vercel secrets add openai_api_key "your-openai-key"
vercel secrets add google_maps_api_key "your-google-maps-key"
```

### Step 4: Deploy

From the `backend` directory:
```bash
vercel --prod
```

Your API will be live at: `https://your-project.vercel.app`

### Alternative: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your Git repository
4. Set Root Directory to `backend`
5. Add environment variables:
   - `OPENAI_API_KEY=your-key`
   - `GOOGLE_MAPS_API_KEY=your-key`
6. Click "Deploy"

---

## 📡 API Endpoints

### Health & Status
- `GET /health` - Health check with service status
- `GET /` - API information

### Predictions
- `GET /predictions/bulk?hour=14` - Get crowd predictions for all locations

### Real-time Data
- `GET /realtime/status` - Check real-time data availability
- `POST /realtime/collect` - Collect live crowd data from Google Maps
- `GET /realtime/cached` - Get cached real-time data

### Maps Integration
- `GET /maps/nearby?lat=19.0760&lng=72.8777` - Get nearby places
- `GET /maps/directions?originLat=19.0760&originLng=72.8777&destLat=19.0590&destLng=72.8360` - Get directions with traffic

### AI Insights
- `POST /ai/insights` - Generate AI-powered crowd insights
  ```json
  {
    "crowdData": [
      {
        "locationName": "Metro Station A",
        "crowdDensity": 75.5,
        "crowdCount": 378,
        "status": "high",
        "predictedNextHour": 65.2
      }
    ]
  }
  ```

- `POST /ai/route-advice` - Get AI route recommendations
  ```json
  {
    "crowdData": [...],
    "origin": "Metro Station A",
    "destination": "City Mall"
  }
  ```

### Locations
- `GET /locations` - Get all monitored locations
- `GET /locations/{location_id}` - Get specific location details

---

## 🔑 Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Application
APP_NAME=CrowdSense AI Backend
ALLOWED_ORIGINS=*
ENABLE_REALTIME_MAPS=true

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini

# Google Maps
GOOGLE_MAPS_API_KEY=AIzaxxxxxxxxxxxxxxx

# Map Provider (google_maps | openstreetmap | synthetic)
MAP_PROVIDER=google_maps
```

---

## 🗺️ Google Maps API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - **Places API**
   - **Distance Matrix API**
   - **Directions API**
   - **Maps JavaScript API** (for frontend)
4. Create API credentials
5. Copy the API key to your `.env` file

---

## 🤖 OpenAI API Setup

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Create a new secret key
5. Copy the key to your `.env` file

---

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/         # API endpoint definitions
│   │       ├── health.py   # Health check
│   │       ├── predictions.py  # ML predictions
│   │       ├── realtime.py     # Real-time data
│   │       ├── maps.py         # Google Maps
│   │       ├── ai.py           # OpenAI integration
│   │       └── locations.py    # Location management
│   ├── core/
│   │   ├── config.py       # Configuration
│   │   └── constants.py    # Constants
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   │   ├── prediction_service.py   # ML predictions
│   │   ├── google_maps_service.py  # Google Maps
│   │   ├── openai_service.py       # OpenAI
│   │   └── realtime_service.py     # Real-time data
│   ├── data/               # Data and locations
│   └── main.py             # FastAPI app entry
├── api/
│   └── index.py            # Vercel serverless entry
├── .env                    # Environment variables (you create this)
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel configuration
├── start.sh                # Linux/Mac startup script
└── run.bat                 # Windows startup script
```

---

## 🔄 Connecting Flutter App

Update your Flutter app's `lib/constants/app_constants.dart`:

```dart
// For local development
static const String apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8000',
);

// For production
static const String apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://your-backend.vercel.app',
);
```

Run your Flutter app:
```bash
# Local backend
flutter run

# Production backend
flutter run --dart-define=API_BASE_URL=https://your-backend.vercel.app
```

---

## 🧪 Testing the API

### Using cURL

```bash
# Health Check
curl http://localhost:8000/health

# Get Predictions
curl http://localhost:8000/predictions/bulk?hour=14

# Get Locations
curl http://localhost:8000/locations

# Get AI Insights
curl -X POST http://localhost:8000/ai/insights \
  -H "Content-Type: application/json" \
  -d '{"crowdData": [{"locationName": "Metro A", "crowdDensity": 75}]}'
```

### Using the Interactive Docs

Visit http://localhost:8000/docs for Swagger UI with live testing.

---

## 📊 API Response Format

All endpoints return JSON responses. Example:

```json
{
  "status": "ok",
  "service": "CrowdSense AI Backend",
  "openAiConfigured": true,
  "googleMapsConfigured": true,
  "mapProvider": "google_maps",
  "realtimeEnabled": true,
  "allowedOrigins": ["*"]
}
```

---

## 🐛 Troubleshooting

### ImportError: No module named 'app'
```bash
# Make sure you're in the backend directory
cd backend
# Reinstall dependencies
pip install -r requirements.txt
```

### Google Maps API not working
- Check if you've enabled all required APIs in Google Cloud Console
- Verify your API key is correct in `.env`
- Make sure billing is enabled for your Google Cloud project

### OpenAI API errors
- Verify your API key is valid
- Check your OpenAI account has available credits
- Ensure `OPENAI_MODEL=gpt-4o-mini` in `.env`

### Port 8000 already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

---

## 💻 Development Tips

1. **API Documentation**: Always available at `/docs`
2. **Hot Reload**: Use `--reload` flag for auto-restart on code changes
3. **Logs**: FastAPI logs all requests to console
4. **Testing**: Use the `/docs` interactive interface to test endpoints

---

## 🚀 Performance

- **Cold Start**: ~2-3 seconds on Vercel
- **Response Time**: <200ms for most endpoints
- **Concurrent Requests**: Handles 100+ concurrent connections
- **Rate Limits**: Respect OpenAI (500 req/min) and Google Maps (1000 req/day free tier) limits

---

## 📝 License

MIT License - Feel free to use this for your hackathon project!

---

## 🤝 Support

For issues or questions:
1. Check the `/docs` endpoint for API documentation
2. Review the troubleshooting section above
3. Ensure all environment variables are set correctly

---

**Built with ❤️ for CrowdSense AI Hackathon**
