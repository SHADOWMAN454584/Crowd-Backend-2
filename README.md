# 🎯 CrowdSense AI - Complete Documentation Index

Welcome to the CrowdSense AI project! This document will guide you to the right documentation.

---

## 📚 Documentation Quick Links

### For Frontend Developers (Flutter)

1. **[FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)** ⭐ **START HERE**
   - Complete API integration guide
   - All endpoints with examples
   - Flutter code samples
   - Request/response formats
   - Error handling

2. **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)**
   - Quick lookup for endpoints
   - Response models
   - Status codes

3. **[ARCHITECTURE.md](./ARCHITECTURE.md)**
   - System overview
   - Data flow diagrams
   - State management
   - Performance tips

### For Backend Developers

1. **[backend/README.md](./backend/README.md)**
   - Complete backend documentation
   - Deployment guide
   - API reference

2. **[backend/START_HERE.md](./backend/START_HERE.md)**
   - Quick start guide
   - One-command setup

---

## 🚀 Quick Start

### Frontend Team

```bash
# 1. Make sure backend is running
cd backend
./run.bat  # Windows
# or
./start.sh  # Mac/Linux

# 2. Update Flutter app
# Edit lib/constants/app_constants.dart
static const String apiBaseUrl = 'http://localhost:8000';

# 3. Read the integration guide
# See FRONTEND_INTEGRATION.md for complete details

# 4. Test the connection
curl http://localhost:8000/health
```

### Backend Team

```bash
# Run the backend
cd backend
./run.bat  # Windows - ONE COMMAND!

# Server will start at:
# http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## 📡 API Endpoints Overview

### Essential Endpoints

```
GET  /health                          # Check backend status
GET  /locations                       # Get all locations
GET  /predictions/bulk?hour=14        # Get crowd predictions
POST /realtime/collect                # Get live data from Google Maps
POST /ai/insights                     # Get AI-powered insights
POST /maps/directions                 # Get directions with traffic
```

**Full details:** [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)

---

## 🏗️ System Architecture

```
┌──────────────┐         ┌──────────────┐
│ Flutter App  │ ◄─────► │ FastAPI      │
│              │  HTTP   │ Backend      │
│ User sees:   │         │              │
│ • Crowds     │         │ Provides:    │
│ • Maps       │         │ • ML Model   │
│ • AI Tips    │         │ • Google API │
└──────────────┘         │ • OpenAI API │
                         └──────────────┘
```

**Full diagrams:** [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 🔌 Integration Checklist

### ✅ Backend Setup
- [ ] Backend running on port 8000
- [ ] OpenAI API key configured
- [ ] Google Maps API key configured
- [ ] `/health` endpoint returns 200

### ✅ Frontend Setup
- [ ] ApiService implemented
- [ ] Base URL configured
- [ ] Can reach `/health`
- [ ] CrowdData model matches API
- [ ] Error handling implemented

### ✅ Testing
- [ ] Health check works
- [ ] Predictions load
- [ ] Real-time data works
- [ ] AI insights generate
- [ ] Maps integration works

---

## 📂 Project Structure

```
PopulationDensity2/
├── backend/                          # FastAPI Backend
│   ├── app/                          # Application code
│   │   ├── api/routes/              # API endpoints
│   │   ├── services/                # Business logic
│   │   ├── models/                  # Data models
│   │   └── main.py                  # Entry point
│   ├── .env                         # API keys (DO NOT COMMIT!)
│   ├── requirements.txt             # Python dependencies
│   ├── vercel.json                  # Vercel config
│   ├── run.bat                      # Windows start
│   ├── start.sh                     # Mac/Linux start
│   └── README.md                    # Backend docs
│
├── FRONTEND_INTEGRATION.md          # ⭐ Main integration guide
├── API_QUICK_REFERENCE.md           # Quick API lookup
├── ARCHITECTURE.md                  # System architecture
└── README.md                        # This file
```

---

## 🎯 Common Tasks

### Start Backend Locally
```bash
cd backend
./run.bat  # Windows
./start.sh  # Mac/Linux
```

### Test API Connection
```bash
curl http://localhost:8000/health
curl http://localhost:8000/predictions/bulk?hour=14
```

### Deploy to Vercel
```bash
vercel secrets add openai_api_key "your-key"
vercel secrets add google_maps_api_key "your-key"
deploy-vercel.bat
```

### Connect Flutter App (Local)
```dart
// lib/constants/app_constants.dart
static const String apiBaseUrl = 'http://localhost:8000';
```

### Connect Flutter App (Production)
```dart
static const String apiBaseUrl = 'https://your-app.vercel.app';
```

---

## 📊 API Response Example

```dart
// GET /predictions/bulk?hour=14

{
  "hour": 14,
  "data": [
    {
      "locationId": "loc-central-station",
      "locationName": "Central Railway Station",
      "latitude": 23.8103,
      "longitude": 90.4125,
      "crowdCount": 310,
      "crowdDensity": 62.0,
      "status": "high",
      "timestamp": "2026-03-27T14:30:00Z",
      "predictedNextHour": 68.5
    }
  ]
}
```

**More examples:** [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md#predictions)

---

## 🆘 Troubleshooting

### Backend not starting?
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Flutter can't connect?
1. Check backend is running: `curl http://localhost:8000/health`
2. Check URL in `app_constants.dart`
3. Check CORS is enabled (it is by default)

### Google Maps not working?
1. Check `backend/.env` has `GOOGLE_MAPS_API_KEY`
2. Enable these APIs in Google Cloud Console:
   - Places API
   - Directions API
   - Distance Matrix API

### OpenAI not working?
1. Check `backend/.env` has `OPENAI_API_KEY`
2. Verify key is valid at platform.openai.com
3. Check you have credits available

---

## 🔑 Environment Setup

### Backend (.env file)
```bash
# backend/.env
OPENAI_API_KEY=sk-proj-xxxxx
GOOGLE_MAPS_API_KEY=AIzaxxxxx
ENABLE_REALTIME_MAPS=true
MAP_PROVIDER=google_maps
ALLOWED_ORIGINS=*
```

⚠️ **Never commit .env file to git!** It's already in .gitignore.

---

## 📱 Flutter Models

Your existing models already match the API perfectly:

```dart
class CrowdData {
  final String locationId;
  final String locationName;
  final double latitude;
  final double longitude;
  final int crowdCount;
  final double crowdDensity;
  final String status;
  final DateTime timestamp;
  final double? predictedNextHour;
}
```

✅ No changes needed! Just connect to the API.

---

## 🌐 URLs

### Local Development
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Production (After Vercel Deploy)
- Backend: https://your-app.vercel.app
- API Docs: https://your-app.vercel.app/docs
- Health: https://your-app.vercel.app/health

---

## ⚡ Performance Tips

1. **Cache responses** - Don't fetch same data repeatedly
2. **Debounce refreshes** - Wait 2 seconds before refreshing
3. **Use real-time sparingly** - It uses Google Maps API quota
4. **Lazy load AI** - Only fetch insights when user needs them
5. **Auto-refresh interval** - 30 seconds is optimal

---

## 📞 Support

### Documentation
- **Full Integration Guide**: [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)
- **Quick Reference**: [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Backend Docs**: [backend/README.md](./backend/README.md)

### Testing
- Interactive API Docs: http://localhost:8000/docs
- Test endpoints with cURL or Postman
- Check backend logs in terminal

---

## ✨ Features

### Backend Provides:
✅ ML-powered crowd predictions (scikit-learn)
✅ Real-time data from Google Maps
✅ AI insights via OpenAI GPT-4
✅ Location-based services
✅ Traffic and directions
✅ 24-hour forecasting
✅ RESTful API with CORS

### Flutter App Uses:
✅ Crowd density visualization
✅ Interactive maps
✅ Analytics and charts
✅ AI-powered recommendations
✅ Smart route suggestions
✅ Best time finder
✅ Real-time alerts

---

## 🎉 You're Ready!

1. **Backend Team**: Backend is complete and deployed to GitHub
2. **Frontend Team**: Read [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) for integration
3. **Both Teams**: Use [API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md) for quick lookup

**Next Steps:**
1. Start backend: `cd backend && ./run.bat`
2. Read integration guide: [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)
3. Implement ApiService in Flutter
4. Test the connection
5. Deploy when ready

---

**Built with ❤️ for CrowdSense AI Hackathon**

**Questions?** Check the docs above or run `./run.bat` and visit http://localhost:8000/docs
