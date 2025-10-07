# Field Management API Documentation

## Base URL
`http://127.0.0.1:8000/api/fields/`

**Authentication:** Required for all endpoints (JWT Bearer token)

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/fields/` | List user's fields |
| POST | `/api/fields/` | Create new field |
| GET | `/api/fields/{id}/` | Get field details |
| PUT | `/api/fields/{id}/` | Full update field |
| PATCH | `/api/fields/{id}/` | Partial update field |
| DELETE | `/api/fields/{id}/` | Delete field |
| PATCH | `/api/fields/{id}/update-moisture/` | Update soil moisture only |
| GET | `/api/fields/{id}/ai-input/` | Get AI model input data |
| GET | `/api/fields/statistics/` | Get user's field statistics |

---

## 1. List Fields

**Endpoint:** `GET /api/fields/`

**Description:** Retrieve all fields belonging to the authenticated user.

**Query Parameters:**
- `is_active` (optional): Filter by active status (`true`/`false`)
- `crop_type` (optional): Filter by crop type (`Maize`, `Wheat`, `Rice`, etc.)
- `region` (optional): Filter by region (`lusaka`, `central`, etc.)
- `search` (optional): Search by name or location

**Example Request:**
```bash
GET /api/fields/?is_active=true&crop_type=Maize
Authorization: Bearer <access_token>
```

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "North Field",
    "crop_type": "Maize",
    "crop_type_display": "Maize",
    "region": "lusaka",
    "region_display": "Lusaka",
    "area": "2.50",
    "crop_age_weeks": 8,
    "current_soil_moisture": 45,
    "is_active": true,
    "created_at": "2025-10-07T10:30:00Z"
  }
]
```

---

## 2. Create Field

**Endpoint:** `POST /api/fields/`

**Description:** Create a new field for the authenticated user.

**Request Body:**
```json
{
  "name": "South Field",
  "location": "Chilanga District, Lusaka",
  "region": "lusaka",
  "latitude": -15.5487,
  "longitude": 28.2819,
  "area": 3.5,
  "crop_type": "Maize",
  "planting_date": "2025-10-01",
  "soil_type": "Loam",
  "current_soil_moisture": 50,
  "irrigation_method": "drip",
  "current_season": "Wet",
  "notes": "High-yield variety planted",
  "is_active": true
}
```

**Required Fields:**
- `name` (string, max 100 characters)
- `region` (string, choices: `lusaka`, `central`, `southern`, etc.)
- `area` (decimal, > 0.01 hectares)
- `crop_type` (string, choices: `Maize`, `Wheat`, `Rice`, `Tomatoes`, `Potatoes`, `Cotton`)
- `planting_date` (date, cannot be in future)
- `soil_type` (string, choices: `Clay`, `Loam`, `Sandy`, `Silty`)

**Optional Fields:**
- `location` (string)
- `latitude` (decimal, -90 to 90)
- `longitude` (decimal, -180 to 180)
- `current_soil_moisture` (integer, 0-100, default: 50)
- `irrigation_method` (string, default: `rainfed`)
- `current_season` (string, default: `Dry`)
- `notes` (text)
- `is_active` (boolean, default: true)

**Example Response:**
```json
{
  "id": 2,
  "user_email": "farmer@test.com",
  "user_name": "Test Farmer",
  "name": "South Field",
  "location": "Chilanga District, Lusaka",
  "region": "lusaka",
  "region_display": "Lusaka",
  "latitude": "-15.548700",
  "longitude": "28.281900",
  "area": "3.50",
  "crop_type": "Maize",
  "crop_type_display": "Maize",
  "planting_date": "2025-10-01",
  "crop_days": 6,
  "crop_age_weeks": 0,
  "soil_type": "Loam",
  "soil_type_display": "Loam",
  "current_soil_moisture": 50,
  "irrigation_method": "drip",
  "irrigation_method_display": "Drip Irrigation",
  "current_season": "Wet",
  "season_display": "Wet Season (November-April)",
  "notes": "High-yield variety planted",
  "is_active": true,
  "created_at": "2025-10-07T15:30:00Z",
  "updated_at": "2025-10-07T15:30:00Z"
}
```

**Validation Errors:**
```json
{
  "area": ["Area must be greater than 0."],
  "planting_date": ["Planting date cannot be in the future."],
  "current_soil_moisture": ["Soil moisture must be between 0 and 100."]
}
```

---

## 3. Get Field Details

**Endpoint:** `GET /api/fields/{id}/`

**Description:** Retrieve detailed information about a specific field.

**Example Request:**
```bash
GET /api/fields/2/
Authorization: Bearer <access_token>
```

**Example Response:** (Same as create response)

**Error Response (Field not found or not owned by user):**
```json
{
  "detail": "Not found."
}
```

---

## 4. Update Field (Full)

**Endpoint:** `PUT /api/fields/{id}/`

**Description:** Fully update a field (all fields required).

**Request Body:** (Same as create, all fields required)

---

## 5. Update Field (Partial)

**Endpoint:** `PATCH /api/fields/{id}/`

**Description:** Partially update a field (only include fields to change).

**Example Request:**
```json
{
  "current_soil_moisture": 35,
  "notes": "Rainfall received, soil moisture decreased"
}
```

**Example Response:**
```json
{
  "id": 2,
  "name": "South Field",
  "current_soil_moisture": 35,
  "notes": "Rainfall received, soil moisture decreased",
  "updated_at": "2025-10-07T16:00:00Z"
  // ... other fields
}
```

---

## 6. Delete Field

**Endpoint:** `DELETE /api/fields/{id}/`

**Description:** Delete a field (only owner can delete).

**Example Request:**
```bash
DELETE /api/fields/2/
Authorization: Bearer <access_token>
```

**Example Response:**
```json
{
  "detail": "Field deleted successfully."
}
```

**Error Response (Not owner):**
```json
{
  "detail": "You do not have permission to delete this field."
}
```

---

## 7. Update Soil Moisture

**Endpoint:** `PATCH /api/fields/{id}/update-moisture/`

**Description:** Quickly update only the soil moisture value.

**Request Body:**
```json
{
  "current_soil_moisture": 42
}
```

**Example Response:**
```json
{
  "id": 2,
  "name": "South Field",
  "current_soil_moisture": 42,
  "updated_at": "2025-10-07T16:15:00Z"
  // ... full field data
}
```

**Validation:**
- `current_soil_moisture` must be between 0 and 100

---

## 8. Get AI Model Input

**Endpoint:** `GET /api/fields/{id}/ai-input/`

**Description:** Get formatted data for AI model prediction.

**Query Parameters:**
- `temperature` (optional, default: 25): Temperature in °C
- `humidity` (optional, default: 60): Humidity in %
- `rainfall` (optional, default: 0): Rainfall in mm
- `windspeed` (optional, default: 10): Wind speed in km/h

**Example Request:**
```bash
GET /api/fields/2/ai-input/?temperature=28&humidity=55&rainfall=0&windspeed=12
Authorization: Bearer <access_token>
```

**Example Response:**
```json
{
  "field_id": 2,
  "field_name": "South Field",
  "ai_model_input": {
    "CropType": "Maize",
    "CropDays": 6,
    "SoilMoisture": 42,
    "temperature": 28.0,
    "humidity": 55.0,
    "rainfall": 0.0,
    "windspeed": 12.0,
    "soilType": "Loam",
    "region": "Lusaka",
    "season": "Wet"
  },
  "weather_data_source": "query_params"
}
```

**Use Case:** This endpoint prepares all 10 features required by the AI irrigation model.

---

## 9. Get Statistics

**Endpoint:** `GET /api/fields/statistics/`

**Description:** Get summary statistics for all user's fields.

**Example Request:**
```bash
GET /api/fields/statistics/
Authorization: Bearer <access_token>
```

**Example Response:**
```json
{
  "total_fields": 5,
  "active_fields": 4,
  "inactive_fields": 1,
  "total_area_hectares": 12.75,
  "crop_distribution": {
    "Maize": 3,
    "Wheat": 1,
    "Tomatoes": 1
  },
  "region_distribution": {
    "Lusaka": 2,
    "Central Province": 2,
    "Southern Province": 1
  }
}
```

---

## Field Choice Values

### Regions (Zambian Provinces)
- `lusaka` - Lusaka
- `central` - Central Province
- `southern` - Southern Province
- `eastern` - Eastern Province
- `copperbelt` - Copperbelt
- `northern` - Northern Province
- `western` - Western Province
- `luapula` - Luapula
- `muchinga` - Muchinga
- `northwestern` - North-Western

### Crop Types
- `Maize` - Maize
- `Wheat` - Wheat
- `Rice` - Rice
- `Tomatoes` - Tomatoes
- `Potatoes` - Potatoes
- `Cotton` - Cotton

### Soil Types
- `Clay` - Clay
- `Loam` - Loam
- `Sandy` - Sandy
- `Silty` - Silty

### Irrigation Methods
- `drip` - Drip Irrigation
- `sprinkler` - Sprinkler Irrigation
- `flood` - Flood/Furrow Irrigation
- `rainfed` - Rain-fed (No Irrigation)

### Seasons
- `Dry` - Dry Season (May-October)
- `Wet` - Wet Season (November-April)

---

## Authentication

All endpoints require JWT authentication:

```bash
Authorization: Bearer <access_token>
```

Get access token from login:
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "email": "farmer@test.com",
  "password": "password123"
}
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 400 Bad Request
```json
{
  "field_name": ["Error message"],
  "another_field": ["Another error message"]
}
```

---

## Testing with cURL

### List Fields
```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/fields/
```

### Create Field
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Field","region":"lusaka","area":2.5,"crop_type":"Maize","planting_date":"2025-10-01","soil_type":"Loam"}' \
  http://127.0.0.1:8000/api/fields/
```

### Update Soil Moisture
```bash
curl -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"current_soil_moisture":38}' \
  http://127.0.0.1:8000/api/fields/1/update-moisture/
```

---

**Last Updated:** October 7, 2025  
**API Version:** 1.0  
**Django Version:** 4.2.7  
**DRF Version:** 3.14.0
