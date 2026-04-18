# Cricket Heroes - Player Dashboard

A FastAPI-based web application for managing and viewing cricket player statistics with a modern, responsive UI.

## Features

✅ **Control Panel** - Select and manage the current player
✅ **Player Stats API** - Get detailed player statistics by ID
✅ **Search Functionality** - Search players by name
✅ **Real-time Updates** - Instant feedback with success/error messages
✅ **Responsive Design** - Works on desktop, tablet, and mobile devices
✅ **Error Handling** - Comprehensive error handling with user-friendly messages
✅ **MongoDB Integration** - Store and retrieve player data

## Project Structure

```
/app
  main.py                    # FastAPI application entry point
  /routes
    __init__.py             # Routes package
    api.py                  # Player statistics API endpoints
    admin.py                # Control panel endpoints
  /templates
    dashboard.html          # Main UI template
  /static
    style.css              # CSS styling
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory with your MongoDB connection string:

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/bbl_season_4
```

A template `.env.example` file is provided with placeholders.

### 3. Run the Application

```bash
cd app
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: **http://localhost:8000/dashboard/bbl4**

## API Endpoints

### Admin Endpoints (`/admin`)

#### Get All Players
```
GET /admin/players
```
Returns a list of all available players in the database.

#### Get Current Player
```
GET /admin/current-player
```
Returns the currently selected player.

#### Select Player
```
POST /admin/select-player
Content-Type: application/json

{
  "player_id": "774977",
  "player_name": "Purushotham"
}
```
Updates the current player in the database.

#### Reset Player Selection
```
DELETE /admin/reset-player
```
Clears the current player selection.

---

### Player Stats Endpoints (`/api`)

#### Get Player Stats
```
GET /api/player-stats/{player_id}
```
Returns detailed statistics for a specific player.

**Example:**
```
GET /api/player-stats/774977
```

#### Get Player Summary
```
GET /api/player-summary/{player_id}
```
Returns a summary of player information (name, role, team, basic stats).

#### Search Players
```
GET /api/search?query={player_name}
```
Search for players by name (case-insensitive).

**Example:**
```
GET /api/search?query=Purushotham
```

#### Get Current Player Stats
```
GET /api/current-player-stats
```
Get the statistics of the currently selected player. This endpoint:
1. Checks the `selected_player` collection for the current player ID
2. Fetches that player's full statistics from the `players` collection
3. Returns the complete player data, or a "no player selected" message

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "playerId": "774977",
    "playerName": "Purushotham",
    "role": "Batsman",
    "stats": { ... }
  }
}
```

---

### Health Check
```
GET /health
```
Returns API status.

## Database Schema

### Players Collection
Expected structure:
```json
{
  "_id": ObjectId,
  "player_id": "774977",
  "player_name": "Purushotham",
  "role": "Batsman",
  "team": "Team Name",
  "country": "Country",
  "stats": {
    "matches": 10,
    "runs": 500,
    "wickets": 0
  }
}
```

### Config Collection
Used to store application configuration (current player selection):
```json
{
  "_id": "current_player",
  "player_id": "774977",
  "player_name": "Purushotham",
  "updated_at": ISODate
}
```

## Features Detailed

### 1. Control Panel
- Search players by name with real-time suggestions
- View current player selection
- One-click player selection
- Reset player selection button
- Success/error notifications

### 2. Player Statistics
- Displays all available player data
- Formatted stat cards with hover effects
- Handles nested JSON data
- Automatic refresh when player is selected

### 3. Error Handling
- HTTP status codes (400, 404, 500)
- User-friendly error messages
- Automatic message dismissal after 4-5 seconds
- Loading indicators during async operations

### 4. Responsive UI
- Mobile-first design
- Grid layout that adapts to screen size
- Touch-friendly buttons and inputs
- Optimized for screens 480px to 1400px+

## Frontend Features

- **Real-time Search**: Debounced input (300ms) to prevent excessive API calls
- **Auto-dismiss Messages**: Success/error messages auto-close after 4-5 seconds
- **Loading States**: Spinner shows during API requests
- **Smooth Animations**: Transitions and slide-in effects
- **Accessible Design**: Semantic HTML, proper labels, keyboard navigation

## Troubleshooting

### MongoDB Connection Error
- Verify MongoDB connection string
- Check if database and collections exist
- Ensure network connectivity

### Port Already in Use
Change the port in `main.py`:
```bash
uvicorn main:app --port 8001
```

### CORS Issues
If accessing from a different domain, add CORS middleware to `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Development

### API Documentation
Once running, visit: **http://localhost:8000/docs**
This provides an interactive API documentation via Swagger UI.

### Alternative API Docs
**http://localhost:8000/redoc**
ReDoc documentation view.

## License

This project is part of Cricket Heroes Analytics.
