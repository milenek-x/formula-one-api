
# 🏎️ F1 Stats API

A Flask-based RESTful API for Formula 1 data including race schedules, drivers, teams, and sessions. Data is periodically scraped and cached in Firebase Firestore for fast, consistent access.

**Base URL:** `https://formula-one-api.vercel.app`

---

## 🚀 Features

- 🗓️ Race Schedule
- 🧑‍✈️ Driver Profiles
- 🏎️ Team Info & Stats
- 🧾 Session Data
- ⚡ Firestore Caching (auto-refreshes every 30 minutes)
- 🧼 Manual Cache Clear
- 🔍 Searchable Endpoints

---

## 📦 Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository-url.git
   ```
   
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
3. Set up Firebase credentials by creating a `.env` file and adding your Firebase key:
   ```bash
   FIREBASE_KEY_PATH='your_firebase_key'
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

---

## 🛣️ API Endpoints & Examples

### 📅 Schedule

#### 🔹 Get All Races
```bash
curl https://formula-one-api.vercel.app/api/races
```

**Response:**
```json
[
  {
    "race_id": 22,
    "grand_prix_name": "Las Vegas",
    "location": "FORMULA 1 HEINEKEN LAS VEGAS GRAND PRIX 2025",
    "month": "Nov",
    "date_range": "20-22",
    "link": "https://www.formula1.com/en/racing/2025/las-vegas",
    "round": "ROUND 22",
    "sessions": []
  }
]
```

#### 🔹 Get Race by ID
```bash
curl https://formula-one-api.vercel.app/api/races/22
```

#### 🔹 Search Races
```bash
curl "https://formula-one-api.vercel.app/api/races/search?q=vegas"
```

#### 🔹 Clear Race Cache
```bash
curl -X POST https://formula-one-api.vercel.app/api/races/cache/clear
```

---

### 🧑 Drivers

#### 🔹 Get All Drivers
```bash
curl https://formula-one-api.vercel.app/api/drivers
```

**Sample Response:**
```json
[
  {
    "driver_id": 1,
    "name": "Alexander Albon",
    "nationality": "Thailand",
    "team": "Williams",
    "driver_points": 16,
    "profile_url": "https://www.formula1.com/en/drivers/alexander-albon",
    "profile_data": {
      "Date of birth": "23/03/1996",
      "Grands Prix entered": "106",
      "Highest race finish": "3 (x2)"
    }
  }
]
```

#### 🔹 Get Driver by ID
```bash
curl https://formula-one-api.vercel.app/api/driver/1
```

#### 🔹 Drivers by Team
```bash
curl https://formula-one-api.vercel.app/api/drivers/team/Williams
```

#### 🔹 Sorted by Points
```bash
curl https://formula-one-api.vercel.app/api/drivers/sorted/points
```

#### 🔹 Top 3 Drivers
```bash
curl https://formula-one-api.vercel.app/api/drivers/top3
```

#### 🔹 Search Drivers
```bash
curl "https://formula-one-api.vercel.app/api/drivers/search?q=albon"
```

#### 🔹 Clear Driver Cache
```bash
curl -X POST https://formula-one-api.vercel.app/api/drivers/cache/clear
```

---

### 🏎️ Teams

#### 🔹 Get All Teams
```bash
curl https://formula-one-api.vercel.app/api/teams
```

**Sample Response:**
```json
[
  {
    "team_id": 1,
    "team_name": "Alpine",
    "full_team_name": "BWT Alpine Formula One Team",
    "base": "Enstone, United Kingdom",
    "team_points": 0,
    "world_championships": "2",
    "drivers": ["Pierre Gasly", "Jack Doohan"]
  }
]
```

#### 🔹 Get Team by ID
```bash
curl https://formula-one-api.vercel.app/api/teams/1
```

#### 🔹 Get Team by Driver
```bash
curl "https://formula-one-api.vercel.app/api/teams/driver?name=gasly"
```

#### 🔹 Sort Teams by Points
```bash
curl https://formula-one-api.vercel.app/api/teams/sort
```

#### 🔹 Top 3 Teams
```bash
curl https://formula-one-api.vercel.app/api/teams/top3
```

#### 🔹 Search Teams
```bash
curl "https://formula-one-api.vercel.app/api/teams/search?q=alpine"
```

#### 🔹 Clear Team Cache
```bash
curl -X POST https://formula-one-api.vercel.app/api/teams/cache/clear
```

---

### 📍 Sessions

#### 🔹 Get Race Sessions
```bash
curl https://formula-one-api.vercel.app/api/races/22/sessions
```

**Response:**
```json
[
  {
    "name": "Race",
    "date": "6",
    "start_time": "05:00",
    "end_time": null,
    "month": "Apr"
  },
  {
    "name": "Qualifying",
    "date": "5",
    "start_time": "06:00",
    "end_time": "07:00",
    "month": "Apr"
  },
  {
    "name": "Practice 3",
    "date": "5",
    "start_time": "02:30",
    "end_time": "03:30",
    "month": "Apr"
  },
  {
    "name": "Practice 2",
    "date": "4",
    "start_time": "Highlights and analysis",
    "end_time": null,
    "month": "Apr"
  },
  {
    "name": "Practice 1",
    "date": "4",
    "start_time": "Highlights and analysis",
    "end_time": null,
    "month": "Apr"
  }
]
```

#### 🔹 Clear Session Cache
```bash
curl -X POST https://formula-one-api.vercel.app/api/sessions/cache/clear
```

---

## ❌ Error Response Format

- If a resource is not found:
```json
{ "error": "Driver not found" }
```
or
```json
{ "message": "No matching races found." }
```

---

## 🛡️ Notes

- Cache updates every 30 minutes automatically.
- All `search` endpoints require a `?q=` query parameter.
- Driver names in team queries are case-insensitive (e.g. `gasly`, `Gasly`, `GASLY` all work).
