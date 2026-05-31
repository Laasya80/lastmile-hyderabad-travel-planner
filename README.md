# LastMile - Hyderabad Local Travel Planner

LastMile is a Streamlit-based local travel planner for Hyderabad. It helps users compare metro, bus, auto, cab, bike, walking, and mixed last-mile options with estimated fares, travel time, route maps, user preferences, analytics, and saved routes.

The project is designed as a beginner-friendly Python application while still including real-world concepts such as SQLite persistence, API-based geocoding, OSRM road distance calculation, authentication, dashboards, and recommendation scoring.

## Deployment Link

Live app: `Add your Streamlit Cloud deployment link here`

Example:

```text
https://lastmile-hyderabad.streamlit.app
```

## Screenshots

Add screenshots after deployment or local testing.

```text
screenshots/
+-- home.png
+-- route-results.png
+-- fare-comparison.png
+-- analytics-dashboard.png
+-- login-favorites.png
```

Suggested screenshot sections:

- Home page with route search
- Fare comparison cards and recommendation badges
- Interactive Hyderabad map
- Analytics dashboard
- Login, signup, and favorite routes

## Features

- Search routes between Hyderabad locations
- Type real Hyderabad places using OpenStreetMap Nominatim search
- Find direct routes and 1-transfer routes
- Calculate walking distance and walking time
- Estimate share-auto, local auto, bike, cab, bus, and car fares
- Use real Hyderabad Metro fare slabs from `metro_fares.csv`
- Use OSRM/OpenStreetMap for real road distance and travel time
- Compare transport options in a clean fare comparison table
- Recommend cheapest, fastest, and best preference-matched routes
- User preferences: Cheapest, Fastest, Less walking, Metro preferred, Avoid traffic
- Optional budget limit for recommendations
- Colored recommendation badges
- Transport type icon chips
- Interactive Folium map with OpenStreetMap tiles
- Analytics dashboard with charts and KPIs
- Signup and login using SQLite
- Save favorite routes for logged-in users
- Save user search history
- Dark and light mode UI
- Beginner-friendly code comments

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python |
| UI Framework | Streamlit |
| Database | SQLite |
| Data Analysis | Pandas |
| Maps | Folium, streamlit-folium, OpenStreetMap |
| Geocoding API | OpenStreetMap Nominatim |
| Routing API | OSRM |
| Charts | Streamlit charts |
| Authentication | SQLite users table with salted password hashes |

## Project Structure

```text
Last_maile/
+-- app.py              # Main Streamlit app and UI logic
+-- database.py         # SQLite tables, route data, auth, history, favorites
+-- lastmile.db         # Local SQLite database
+-- metro_fares.csv     # Hyderabad Metro fare slabs
+-- requirements.txt    # Python dependencies
+-- README.md           # Project documentation
```

## Installation Guide

1. Clone the repository:

```powershell
git clone https://github.com/YOUR-USERNAME/lastmile-hyderabad-travel-planner.git
cd lastmile-hyderabad-travel-planner
```

2. Create a virtual environment:

```powershell
python -m venv venv
```

3. Activate the virtual environment:

```powershell
venv\Scripts\activate
```

On macOS or Linux:

```bash
source venv/bin/activate
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Run the app:

```powershell
streamlit run app.py
```

6. Open the local app:

```text
http://localhost:8501
```

## Requirements

```text
streamlit
folium
streamlit-folium
requests
pandas
```

SQLite is included with Python, so no separate SQLite installation is required.

## Architecture Explanation

LastMile uses a simple layered architecture:

```text
User Interface
    |
    v
Streamlit app.py
    |
    +-- Route search and recommendation logic
    +-- Fare comparison logic
    +-- Analytics dashboard
    +-- Authentication UI
    +-- Folium map rendering
    |
    v
database.py
    |
    +-- SQLite tables
    +-- Sample Hyderabad stops and routes
    +-- User accounts
    +-- Search history
    +-- Favorite routes
    |
    v
External APIs
    |
    +-- Nominatim for location search
    +-- OSRM for road distance and travel time
```

### Database Tables

- `stops`: stores Hyderabad stop names and area types.
- `routes`: stores sample route distance, mode, fare, and time.
- `users`: stores usernames, password hashes, and salts.
- `user_search_history`: stores searches made by logged-in users.
- `favorite_routes`: stores saved routes for logged-in users.

### Recommendation Engine

The recommendation engine scores each transport option using:

- Cost
- Travel time
- Walking distance
- Transport changes
- Traffic risk
- Metro preference
- Budget fit

The score changes based on the selected user preference. Lower score means a better match.

## API Explanation

### Nominatim API

Nominatim is used to convert typed Hyderabad place names into latitude and longitude.

Example use:

```text
User types: Charminar
Nominatim returns: latitude, longitude, display name
```

The app then maps the searched real-world place to the nearest known sample stop for route planning.

### OSRM API

OSRM is used to calculate real road distance and estimated travel time using latitude and longitude.

Supported route profiles:

- `driving`
- `walking`

Example:

```text
From coordinates -> To coordinates
OSRM returns:
- distance in meters
- duration in seconds
```

The app converts these values into kilometers and minutes for display.

### Fare Model

LastMile uses a hybrid fare model:

- Metro fares come from `metro_fares.csv`.
- Bus fares are estimated by distance/stages.
- App-based rides are estimated using fare formulas.
- App fares include a disclaimer because real prices can vary due to demand, surge, waiting charges, and availability.

## Analytics Dashboard

The dashboard shows:

- Most searched routes
- Average trip cost
- Average travel time
- Popular transport modes
- Cheapest routes in Hyderabad
- Route data summary table

Search analytics are session-based for guests and database-backed for logged-in users.

## Authentication

LastMile includes a simple local authentication system:

- Signup
- Login
- Logout
- Salted password hashing
- Saved search history
- Favorite routes

This is suitable for a beginner project and local/demo use. For production, use a dedicated authentication provider or a more complete security implementation.

## Future Improvements

- Add live public transport APIs if official APIs become available
- Add real-time traffic data
- Add route geometry lines from OSRM on the map
- Add user profile page
- Add password reset flow
- Add cloud database support
- Add route export/share feature
- Add mobile PWA support
- Add more Hyderabad stops and routes
- Add tests for route scoring and database helpers

## GitHub Setup

```powershell
git init
git add app.py database.py metro_fares.csv requirements.txt README.md
git commit -m "Create LastMile Hyderabad travel planner"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/lastmile-hyderabad-travel-planner.git
git push -u origin main
```

## License

Add your preferred license here, such as MIT License.

