# 🔌 Quick API Reference Card

Quick lookup for CrowdSense AI Backend endpoints.

---

## 📍 Base URL
```dart
http://localhost:8000              // Local
https://your-app.vercel.app        // Production
```

---

## 🚀 Quick Endpoints

### Health
```http
GET /health
```

### Locations
```http
GET /locations
```

### Predictions
```http
GET /predictions/bulk?hour=14
```

### Real-time
```http
GET  /realtime/status
POST /realtime/collect
GET  /realtime/cached
```

### Google Maps
```http
GET  /maps/nearby?latitude=23.81&longitude=90.41&radius=1000
POST /maps/directions
GET  /maps/place/{place_id}
GET  /maps/estimate-crowd/{location_id}?latitude=23.81&longitude=90.41
```

### AI (OpenAI)
```http
POST /ai/insights
POST /ai/route-advice
```

### Smart Route
```http
POST /smart-route/nearby
```

---

## 📊 Response Models

### CrowdData (Predictions Response)
```json
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
```

### Location
```json
{
  "id": "loc-central-station",
  "name": "Central Railway Station",
  "latitude": 23.8103,
  "longitude": 90.4125,
  "category": "transport",
  "tags": ["commuter", "transit"],
  "baselineDensityProfile": {"0": 18.0, "23": 30.0}
}
```

### Smart Route Nearby
```json
{
  "radius_km": 12,
  "nearby_locations": [
    {
      "location_id": "loc-central-station",
      "location_name": "Central Railway Station",
      "distance_km": 1.2,
      "predicted_density": 78.4,
      "status": "high"
    }
  ],
  "suggestions": [
    {
      "original_location_id": "loc-central-station",
      "original_location_name": "Central Railway Station",
      "original_density": 78.4,
      "original_distance_km": 1.2,
      "alternative_location_id": "loc-gulshan-circle",
      "alternative_location_name": "Gulshan Circle",
      "alternative_density": 34.2,
      "alternative_distance_km": 4.9,
      "savings": 44.2,
      "fastest_route_minutes": 17.0,
      "fastest_route_distance_km": 6.3,
      "route_source": "google_maps",
      "selection_source": "openai",
      "ai_reason": "This route is the fastest among lower-density options."
    }
  ]
}
```

---

## 🎯 Flutter Quick Start

```dart
// 1. Check backend
final health = await http.get(Uri.parse('$baseUrl/health'));

// 2. Get predictions
final response = await http.get(
  Uri.parse('$baseUrl/predictions/bulk?hour=14')
);
final data = json.decode(response.body);
final crowdList = (data['data'] as List)
    .map((item) => CrowdData.fromJson(item))
    .toList();

// 3. Get AI insights
final insights = await http.post(
  Uri.parse('$baseUrl/ai/insights'),
  headers: {'Content-Type': 'application/json'},
  body: json.encode({'crowdData': crowdList.map((c) => c.toJson()).toList()}),
);
```

---

## ⚡ Status Codes

- `200` - Success
- `400` - Bad request
- `404` - Not found
- `500` - Server error

---

For detailed documentation, see [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)
