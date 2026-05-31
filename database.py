import hashlib  # Import hashlib so passwords can be stored as hashes instead of plain text.

import secrets  # Import secrets so each password gets a random salt.

import sqlite3  # Import SQLite so Python can create and use a small local database file.

from datetime import datetime  # Import datetime so saved searches and favorites can store when they were created.

DATABASE_NAME = "lastmile.db"  # Store the database file name in one place so it is easy to change later.

AVERAGE_WALKING_SPEED_METERS_PER_MINUTE = 80  # Use 80 meters per minute as a simple average walking speed.

SHARE_AUTO_BASE_FARE = 20  # Use Rs. 20 as the starting share-auto fare for short local rides.

SHARE_AUTO_COST_PER_KM = 12  # Add Rs. 12 for each kilometer in a share-auto estimate.

SHARE_AUTO_SPEED_KM_PER_HOUR = 18  # Use 18 km/h as a simple city traffic speed for share-autos.

MAX_COMFORTABLE_WALK_METERS = 700  # Walk if the nearby distance is short, otherwise suggest share-auto.

NEARBY_ACCESS_DISTANCES = {  # Store sample nearby walking distances from each area to its main stop or pickup point.
    "Ameerpet": 500,  # Use 500 meters for Ameerpet to match a realistic metro-station walk.
    "Dilsukhnagar": 450,  # Use 450 meters for Dilsukhnagar.
    "Secunderabad": 600,  # Use 600 meters for Secunderabad.
    "Hitech City": 300,  # Use 300 meters for Hitech City to match a short destination walk.
    "Kukatpally": 650,  # Use 650 meters for Kukatpally.
    "LB Nagar": 550,  # Use 550 meters for LB Nagar.
    "Miyapur": 750,  # Use 750 meters for Miyapur, which may need a share-auto.
    "Uppal": 700,  # Use 700 meters for Uppal.
    "Mehdipatnam": 800,  # Use 800 meters for Mehdipatnam, which may need a share-auto.
    "Charminar": 900,  # Use 900 meters for Charminar, which may need a share-auto.
    "Gachibowli": 850,  # Use 850 meters for Gachibowli, which may need a share-auto.
    "Jubilee Hills": 650,  # Use 650 meters for Jubilee Hills.
    "Begumpet": 400,  # Use 400 meters for Begumpet.
    "Koti": 500,  # Use 500 meters for Koti.
    "Madhapur": 450,  # Use 450 meters for Madhapur.
}  # End the nearby distance dictionary.

STOP_COORDINATES = {  # Store sample latitude and longitude values for Hyderabad stops.
    "Ameerpet": (17.4375, 78.4483),  # Store the map point for Ameerpet.
    "Dilsukhnagar": (17.3687, 78.5247),  # Store the map point for Dilsukhnagar.
    "Secunderabad": (17.4399, 78.4983),  # Store the map point for Secunderabad.
    "Hitech City": (17.4474, 78.3762),  # Store the map point for Hitech City.
    "Kukatpally": (17.4948, 78.3996),  # Store the map point for Kukatpally.
    "LB Nagar": (17.3457, 78.5522),  # Store the map point for LB Nagar.
    "Miyapur": (17.4965, 78.3618),  # Store the map point for Miyapur.
    "Uppal": (17.4058, 78.5591),  # Store the map point for Uppal.
    "Mehdipatnam": (17.3957, 78.4330),  # Store the map point for Mehdipatnam.
    "Charminar": (17.3616, 78.4747),  # Store the map point for Charminar.
    "Gachibowli": (17.4401, 78.3489),  # Store the map point for Gachibowli.
    "Jubilee Hills": (17.4326, 78.4071),  # Store the map point for Jubilee Hills.
    "Begumpet": (17.4449, 78.4664),  # Store the map point for Begumpet.
    "Koti": (17.3850, 78.4867),  # Store the map point for Koti.
    "Madhapur": (17.4486, 78.3908),  # Store the map point for Madhapur.
}  # End the stop coordinates dictionary.


def get_connection():  # Create a reusable function for opening a database connection.
    connection = sqlite3.connect(DATABASE_NAME)  # Open the SQLite database file, or create it if it does not exist.
    try:  # Try changing the journal mode because OneDrive can sometimes block SQLite journal files.
        connection.execute("PRAGMA journal_mode=OFF")  # Turn off the extra journal file when SQLite allows it.
    except sqlite3.OperationalError:  # Handle rare OneDrive or locking problems with the pragma.
        pass  # Keep using the connection even if SQLite cannot change journal mode right now.
    connection.row_factory = sqlite3.Row  # Return rows that can be read by column name, like row["name"].
    return connection  # Send the open database connection back to the code that asked for it.


def create_tables():  # Create a function that builds the database tables.
    connection = get_connection()  # Open a connection to the SQLite database.
    cursor = connection.cursor()  # Create a cursor, which is used to run SQL commands.

    cursor.execute(  # Run a SQL command that creates the stops table.
        """  -- Start a multi-line SQL query so it is easier to read.
        CREATE TABLE IF NOT EXISTS stops (  -- Create the stops table only if it does not already exist.
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Give every stop a unique number automatically.
            name TEXT NOT NULL UNIQUE,  -- Store the stop name and prevent duplicate stop names.
            area_type TEXT NOT NULL  -- Store a simple category, such as Metro, Bus Hub, or IT Area.
        )  -- End the stops table definition.
        """  # End the multi-line SQL query.
    )  # Finish running the stops table query.

    cursor.execute(  # Run a SQL command that creates the routes table.
        """  -- Start a multi-line SQL query so it is easier to read.
        CREATE TABLE IF NOT EXISTS routes (  -- Create the routes table only if it does not already exist.
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Give every route a unique number automatically.
            from_stop_id INTEGER NOT NULL,  -- Store the starting stop id for this route.
            to_stop_id INTEGER NOT NULL,  -- Store the destination stop id for this route.
            mode TEXT NOT NULL,  -- Store the travel mode, such as Metro, Bus, or Auto.
            distance_km REAL NOT NULL,  -- Store the approximate route distance in kilometers.
            estimated_minutes INTEGER NOT NULL,  -- Store the approximate travel time in minutes.
            fare_rupees INTEGER NOT NULL,  -- Store the approximate fare in Indian rupees.
            route_notes TEXT NOT NULL,  -- Store a simple beginner-friendly route note.
            FOREIGN KEY (from_stop_id) REFERENCES stops (id),  -- Link from_stop_id to the stops table.
            FOREIGN KEY (to_stop_id) REFERENCES stops (id),  -- Link to_stop_id to the stops table.
            UNIQUE (from_stop_id, to_stop_id)  -- Prevent the same route from being inserted twice.
        )  -- End the routes table definition.
        """  # End the multi-line SQL query.
    )  # Finish running the routes table query.

    cursor.execute(  # Run a SQL command that creates the users table.
        """  -- Start a multi-line SQL query for app users.
        CREATE TABLE IF NOT EXISTS users (  -- Create the users table only if it does not already exist.
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Give every user a unique number.
            username TEXT NOT NULL UNIQUE,  -- Store a unique username for login.
            password_hash TEXT NOT NULL,  -- Store the hashed password, not the real password.
            password_salt TEXT NOT NULL,  -- Store the random salt used to hash this password.
            created_at TEXT NOT NULL  -- Store when the account was created.
        )  -- End the users table definition.
        """  # End the multi-line SQL query.
    )  # Finish running the users table query.

    cursor.execute(  # Run a SQL command that creates user search history.
        """  -- Start a multi-line SQL query for saved searches.
        CREATE TABLE IF NOT EXISTS user_search_history (  -- Create the search history table if needed.
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Give every saved search a unique id.
            user_id INTEGER NOT NULL,  -- Store which user made this search.
            from_location TEXT NOT NULL,  -- Store the search starting location.
            to_location TEXT NOT NULL,  -- Store the search destination.
            searched_at TEXT NOT NULL,  -- Store when this search happened.
            FOREIGN KEY (user_id) REFERENCES users (id)  -- Link this search to the users table.
        )  -- End the search history table definition.
        """  # End the multi-line SQL query.
    )  # Finish running the search history table query.

    cursor.execute(  # Run a SQL command that creates favorite routes.
        """  -- Start a multi-line SQL query for favorite routes.
        CREATE TABLE IF NOT EXISTS favorite_routes (  -- Create the favorites table if needed.
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Give every favorite a unique id.
            user_id INTEGER NOT NULL,  -- Store which user owns this favorite.
            from_location TEXT NOT NULL,  -- Store the favorite route starting location.
            to_location TEXT NOT NULL,  -- Store the favorite route destination.
            created_at TEXT NOT NULL,  -- Store when the favorite was saved.
            FOREIGN KEY (user_id) REFERENCES users (id),  -- Link this favorite to the users table.
            UNIQUE (user_id, from_location, to_location)  -- Prevent the same user from saving the same favorite twice.
        )  -- End the favorites table definition.
        """  # End the multi-line SQL query.
    )  # Finish running the favorites table query.

    connection.commit()  # Save the table changes to the database file.
    connection.close()  # Close the database connection because this function is finished.


def add_sample_data():  # Create a function that adds starter stops and routes.
    connection = get_connection()  # Open a connection to the SQLite database.
    cursor = connection.cursor()  # Create a cursor so we can run SQL insert commands.

    stops = [  # Create a list of Hyderabad stops that will be added to the stops table.
        ("Ameerpet", "Metro Interchange"),  # Add Ameerpet as a major metro interchange.
        ("Dilsukhnagar", "Residential and Bus Area"),  # Add Dilsukhnagar as a busy residential and bus area.
        ("Secunderabad", "Railway and Metro Hub"),  # Add Secunderabad as a railway and metro hub.
        ("Hitech City", "IT Area"),  # Add Hitech City as an IT area.
        ("Kukatpally", "Residential and Metro Area"),  # Add Kukatpally as a residential and metro area.
        ("LB Nagar", "Metro Terminal"),  # Add LB Nagar as a metro terminal area.
        ("Miyapur", "Metro Terminal"),  # Add Miyapur as a metro terminal area.
        ("Uppal", "Metro and Stadium Area"),  # Add Uppal as a metro and stadium area.
        ("Mehdipatnam", "Bus Hub"),  # Add Mehdipatnam as a major bus hub.
        ("Charminar", "Heritage Area"),  # Add Charminar as a heritage area.
        ("Gachibowli", "IT and Financial District"),  # Add Gachibowli as an IT and financial district.
        ("Jubilee Hills", "Commercial Area"),  # Add Jubilee Hills as a commercial area.
        ("Begumpet", "Metro and Commercial Area"),  # Add Begumpet as a metro and commercial area.
        ("Koti", "Market and Bus Area"),  # Add Koti as a market and bus area.
        ("Madhapur", "IT and Business Area"),  # Add Madhapur as an IT and business area.
    ]  # End the stops list.

    cursor.executemany(  # Run one insert query many times, once for each stop.
        "INSERT OR IGNORE INTO stops (name, area_type) VALUES (?, ?)",  # Insert a stop, but ignore it if the name already exists.
        stops,  # Give SQLite the list of stop values to insert.
    )  # Finish inserting the stops.

    cursor.execute("SELECT id, name FROM stops")  # Get every stop id and name so route data can use ids instead of text names.
    stop_ids = {row["name"]: row["id"] for row in cursor.fetchall()}  # Build a dictionary like {"Ameerpet": 1}.

    routes = [  # Create a list of realistic sample routes between Hyderabad areas.
        ("Miyapur", "Kukatpally", "Metro", 5.0, 12, 20, "Take the Red Line metro towards LB Nagar."),  # Add a short metro route.
        ("Kukatpally", "Ameerpet", "Metro", 8.0, 18, 30, "Take the Red Line metro towards LB Nagar."),  # Add a metro route to Ameerpet.
        ("Ameerpet", "Begumpet", "Metro", 3.0, 8, 15, "Take the Blue Line metro towards Nagole."),  # Add a short metro route to Begumpet.
        ("Ameerpet", "Hitech City", "Metro", 9.0, 22, 35, "Take the Blue Line metro towards Raidurg."),  # Add a metro route to Hitech City.
        ("Hitech City", "Madhapur", "Auto", 3.0, 12, 80, "Take an auto or short cab ride from the metro area."),  # Add a short last-mile route.
        ("Madhapur", "Gachibowli", "Bus/Cab", 6.0, 20, 120, "Use a local bus, shared auto, or cab through the IT corridor."),  # Add an IT corridor route.
        ("Ameerpet", "Jubilee Hills", "Metro/Auto", 7.0, 20, 60, "Take metro up to Jubilee Hills Check Post, then walk or take an auto."),  # Add a mixed route.
        ("Secunderabad", "Ameerpet", "Metro", 7.0, 16, 30, "Take the Blue Line metro towards Raidurg."),  # Add a metro route from Secunderabad.
        ("Secunderabad", "Uppal", "Metro", 9.0, 20, 35, "Take the Blue Line metro towards Nagole."),  # Add a metro route to Uppal.
        ("Uppal", "LB Nagar", "Bus/Auto", 8.0, 25, 70, "Use a TSRTC bus or shared auto through Nagole."),  # Add an east Hyderabad route.
        ("LB Nagar", "Dilsukhnagar", "Metro", 5.0, 10, 20, "Take the Red Line metro towards Miyapur."),  # Add a metro route near LB Nagar.
        ("Dilsukhnagar", "Koti", "Bus", 7.0, 22, 25, "Take a TSRTC bus towards Koti or Afzalgunj."),  # Add a common bus route.
        ("Koti", "Charminar", "Bus/Auto", 4.0, 18, 50, "Use a local bus or auto through the Old City approach."),  # Add a heritage area route.
        ("Mehdipatnam", "Charminar", "Bus/Auto", 8.0, 28, 70, "Use a bus or auto via Nampally and Afzalgunj."),  # Add a central-to-old-city route.
        ("Mehdipatnam", "Gachibowli", "Bus/Cab", 11.0, 35, 140, "Use a bus or cab via Tolichowki and Shaikpet."),  # Add a west Hyderabad route.
        ("Mehdipatnam", "Ameerpet", "Bus/Metro", 9.0, 30, 50, "Take a bus to Lakdikapul or Ameerpet, depending on availability."),  # Add a route to Ameerpet.
        ("Begumpet", "Secunderabad", "Metro", 5.0, 12, 25, "Take the Blue Line metro towards Nagole."),  # Add a central metro route.
        ("Jubilee Hills", "Madhapur", "Auto/Cab", 5.0, 18, 100, "Take an auto or cab through Road Number 36."),  # Add a nearby commercial route.
        ("Kukatpally", "Hitech City", "Metro", 7.0, 18, 30, "Take the metro and change if needed through Ameerpet."),  # Add a practical route to the IT area.
        ("LB Nagar", "Ameerpet", "Metro", 14.0, 32, 45, "Take the Red Line metro towards Miyapur."),  # Add a longer metro route.
    ]  # End the routes list.

    for route in routes:  # Loop through each route so we can insert it and its return route.
        from_name, to_name, mode, distance_km, minutes, fare, notes = route  # Unpack one route into clear variable names.
        insert_route(cursor, stop_ids, from_name, to_name, mode, distance_km, minutes, fare, notes)  # Insert the forward route.
        insert_route(cursor, stop_ids, to_name, from_name, mode, distance_km, minutes, fare, notes)  # Insert the return route.

    connection.commit()  # Save all inserted stops and routes to the database file.
    connection.close()  # Close the database connection because seeding is finished.


def insert_route(cursor, stop_ids, from_name, to_name, mode, distance_km, minutes, fare, notes):  # Create a helper for inserting one route.
    cursor.execute(  # Run a SQL insert command for one route.
        """  -- Start a multi-line SQL insert query.
        INSERT OR IGNORE INTO routes  -- Insert this route, but skip it if the route already exists.
        (from_stop_id, to_stop_id, mode, distance_km, estimated_minutes, fare_rupees, route_notes)  -- List the columns we want to fill.
        VALUES (?, ?, ?, ?, ?, ?, ?)  -- Use placeholders so Python safely supplies the values.
        """  # End the multi-line SQL insert query.
        ,  # Separate the SQL query from the Python values.
        (stop_ids[from_name], stop_ids[to_name], mode, distance_km, minutes, fare, notes),  # Provide the route values for the placeholders.
    )  # Finish running the route insert query.


def hash_password(password, salt):  # Create a function that turns a password into a safe hash.
    password_text = password + salt  # Combine the password with a random salt before hashing.
    return hashlib.sha256(password_text.encode("utf-8")).hexdigest()  # Return a SHA-256 hash string.


def create_user(username, password):  # Create a function that signs up a new user.
    clean_username = username.strip().lower()  # Clean the username so login is consistent.
    if len(clean_username) < 3:  # Check that the username is long enough.
        return False, "Username must be at least 3 characters."  # Return a friendly validation message.
    if len(password) < 4:  # Check that the password is not too short for this beginner demo.
        return False, "Password must be at least 4 characters."  # Return a friendly validation message.
    salt = secrets.token_hex(16)  # Create a random salt for this user's password.
    password_hash = hash_password(password, salt)  # Hash the password with the salt.
    connection = get_connection()  # Open a database connection.
    cursor = connection.cursor()  # Create a cursor so we can run SQL.
    try:  # Try inserting the user because the username may already exist.
        cursor.execute(  # Run an INSERT query for the new account.
            "INSERT INTO users (username, password_hash, password_salt, created_at) VALUES (?, ?, ?, ?)",  # Use placeholders for safety.
            (clean_username, password_hash, salt, datetime.now().isoformat(timespec="seconds")),  # Provide the user values.
        )  # Finish the INSERT query.
        connection.commit()  # Save the new user to the database.
        return True, "Account created. You can log in now."  # Return success.
    except sqlite3.IntegrityError:  # Handle duplicate usernames.
        return False, "That username already exists."  # Return a friendly duplicate message.
    finally:  # Always close the database connection.
        connection.close()  # Close the database connection.


def authenticate_user(username, password):  # Create a function that checks login details.
    clean_username = username.strip().lower()  # Clean the username the same way signup does.
    connection = get_connection()  # Open a database connection.
    cursor = connection.cursor()  # Create a cursor for SQL.
    cursor.execute("SELECT id, username, password_hash, password_salt FROM users WHERE username = ?", (clean_username,))  # Find this user by username.
    user = cursor.fetchone()  # Read the matching user row, or None.
    connection.close()  # Close the database connection.
    if not user:  # Check whether no user was found.
        return None  # Return no user when the username is unknown.
    entered_hash = hash_password(password, user["password_salt"])  # Hash the entered password with the saved salt.
    if entered_hash == user["password_hash"]:  # Compare hashes instead of comparing plain passwords.
        return {"id": user["id"], "username": user["username"]}  # Return simple user details for the session.
    return None  # Return no user when the password is wrong.


def save_user_search(user_id, from_location, to_location):  # Create a function that saves one user's route search.
    connection = get_connection()  # Open a database connection.
    cursor = connection.cursor()  # Create a cursor for SQL.
    cursor.execute(  # Insert this search into the user_search_history table.
        "INSERT INTO user_search_history (user_id, from_location, to_location, searched_at) VALUES (?, ?, ?, ?)",  # Use placeholders for safety.
        (user_id, from_location, to_location, datetime.now().isoformat(timespec="seconds")),  # Provide the search values.
    )  # Finish the INSERT query.
    connection.commit()  # Save the search.
    connection.close()  # Close the database connection.


def get_user_search_history(user_id, limit=8):  # Create a function that reads one user's saved search history.
    connection = get_connection()  # Open a database connection.
    cursor = connection.cursor()  # Create a cursor for SQL.
    cursor.execute(  # Select recent searches for this user.
        """  -- Start a multi-line SQL query for user search history.
        SELECT from_location, to_location, searched_at  -- Read route labels and time.
        FROM user_search_history  -- Read from the saved search table.
        WHERE user_id = ?  -- Only include searches for this logged-in user.
        ORDER BY searched_at DESC  -- Show newest searches first.
        LIMIT ?  -- Keep the list short for the UI.
        """  # End the multi-line SQL query.
        ,  # Separate SQL from values.
        (user_id, limit),  # Provide the user id and limit.
    )  # Finish the SELECT query.
    rows = [dict(row) for row in cursor.fetchall()]  # Convert rows into dictionaries.
    connection.close()  # Close the database connection.
    return rows  # Return the saved searches.


def save_favorite_route(user_id, from_location, to_location):  # Create a function that saves a favorite route.
    connection = get_connection()  # Open a database connection.
    cursor = connection.cursor()  # Create a cursor for SQL.
    cursor.execute(  # Insert the favorite route, ignoring duplicates.
        "INSERT OR IGNORE INTO favorite_routes (user_id, from_location, to_location, created_at) VALUES (?, ?, ?, ?)",  # Use placeholders for safety.
        (user_id, from_location, to_location, datetime.now().isoformat(timespec="seconds")),  # Provide favorite route values.
    )  # Finish the INSERT query.
    connection.commit()  # Save the favorite route.
    changed_rows = cursor.rowcount  # Read whether SQLite inserted a new row.
    connection.close()  # Close the database connection.
    if changed_rows == 0:  # Check whether this route was already saved.
        return False, "This route is already in your favorites."  # Return a duplicate message.
    return True, "Route saved to favorites."  # Return success.


def get_favorite_routes(user_id):  # Create a function that reads saved favorite routes.
    connection = get_connection()  # Open a database connection.
    cursor = connection.cursor()  # Create a cursor for SQL.
    cursor.execute(  # Select all favorites for this user.
        """  -- Start a multi-line SQL query for favorites.
        SELECT from_location, to_location, created_at  -- Read favorite route details.
        FROM favorite_routes  -- Read from the favorites table.
        WHERE user_id = ?  -- Only include this user's favorites.
        ORDER BY created_at DESC  -- Show newest favorites first.
        """  # End the multi-line SQL query.
        ,  # Separate SQL from values.
        (user_id,),  # Provide the user id.
    )  # Finish the SELECT query.
    rows = [dict(row) for row in cursor.fetchall()]  # Convert rows into dictionaries.
    connection.close()  # Close the database connection.
    return rows  # Return favorite routes.


def initialize_database():  # Create one setup function that the app can call when it starts.
    create_tables()  # Make sure the stops and routes tables exist.
    add_sample_data()  # Add starter Hyderabad stops and routes if they are not already there.


def get_all_stop_names():  # Create a function that returns stop names for dropdown menus.
    connection = get_connection()  # Open a connection to the database.
    cursor = connection.cursor()  # Create a cursor so we can run a select query.
    cursor.execute("SELECT name FROM stops ORDER BY name")  # Select all stop names and sort them alphabetically.
    stops = [row["name"] for row in cursor.fetchall()]  # Turn the database rows into a simple Python list of names.
    connection.close()  # Close the database connection because reading is finished.
    return stops  # Return the list of stop names to the Streamlit app.


def get_stop_coordinates(location_name):  # Create a function that returns map coordinates for one location.
    return STOP_COORDINATES.get(location_name)  # Return the latitude and longitude, or None if the location is missing.


def get_all_stops_for_map():  # Create a function that returns stop details for map markers.
    connection = get_connection()  # Open a connection to the SQLite database.
    cursor = connection.cursor()  # Create a cursor so we can read stop data.
    cursor.execute("SELECT name, area_type FROM stops ORDER BY name")  # Read stop names and categories from the stops table.
    stops = []  # Create an empty list that will hold map-ready stop dictionaries.
    for row in cursor.fetchall():  # Loop through every stop returned by the database.
        coordinates = get_stop_coordinates(row["name"])  # Look up the latitude and longitude for this stop.
        if coordinates:  # Only add the stop to the map if coordinates are available.
            stops.append(  # Add one map marker dictionary to the list.
                {  # Start the stop dictionary.
                    "name": row["name"],  # Store the stop name.
                    "area_type": row["area_type"],  # Store the stop category.
                    "latitude": coordinates[0],  # Store the latitude value.
                    "longitude": coordinates[1],  # Store the longitude value.
                }  # End the stop dictionary.
            )  # Finish adding this stop dictionary.
    connection.close()  # Close the database connection because reading is finished.
    return stops  # Return all map-ready stops to the Streamlit app.


def get_all_route_records():  # Create a function that returns route rows for the analytics dashboard.
    connection = get_connection()  # Open a connection to the SQLite database.
    cursor = connection.cursor()  # Create a cursor so we can run a select query.
    cursor.execute(  # Run a SQL query that joins route ids to readable stop names.
        """  -- Start a multi-line SQL query for dashboard route data.
        SELECT
            from_stop.name AS from_location,  -- Read the route starting location.
            to_stop.name AS to_location,  -- Read the route ending location.
            routes.mode AS mode,  -- Read the transport mode.
            routes.distance_km AS distance_km,  -- Read the route distance.
            routes.estimated_minutes AS estimated_minutes,  -- Read the estimated travel time.
            routes.fare_rupees AS fare_rupees  -- Read the route fare.
        FROM routes  -- Start from the routes table.
        JOIN stops AS from_stop ON routes.from_stop_id = from_stop.id  -- Join to get the From stop name.
        JOIN stops AS to_stop ON routes.to_stop_id = to_stop.id  -- Join to get the To stop name.
        ORDER BY routes.fare_rupees ASC, routes.estimated_minutes ASC  -- Sort low fare first for dashboard use.
        """  # End the multi-line SQL query.
    )  # Finish running the SQL query.
    route_records = [dict(row) for row in cursor.fetchall()]  # Convert SQLite rows into normal Python dictionaries.
    connection.close()  # Close the database connection because reading is finished.
    return route_records  # Return all route dictionaries to the Streamlit app.


def get_nearby_walking_distance(location_name):  # Create a function that finds the nearby first-mile or last-mile distance.
    return NEARBY_ACCESS_DISTANCES.get(location_name, 500)  # Return the saved distance, or use 500 meters as a simple default.


def calculate_walking_time(distance_meters):  # Create a function that converts walking distance into walking minutes.
    minutes = distance_meters / AVERAGE_WALKING_SPEED_METERS_PER_MINUTE  # Divide distance by walking speed to estimate time.
    return round(minutes)  # Round the result so the app shows a simple whole number.


def calculate_share_auto_cost(distance_meters):  # Create a function that estimates share-auto cost from distance.
    distance_km = distance_meters / 1000  # Convert meters into kilometers because auto fares are easier to estimate by km.
    cost = SHARE_AUTO_BASE_FARE + (distance_km * SHARE_AUTO_COST_PER_KM)  # Add base fare plus distance-based fare.
    return round(cost)  # Round the fare so the app shows a clean rupee amount.


def calculate_share_auto_time(distance_meters):  # Create a function that estimates share-auto travel time from distance.
    distance_km = distance_meters / 1000  # Convert meters into kilometers for the speed formula.
    hours = distance_km / SHARE_AUTO_SPEED_KM_PER_HOUR  # Divide distance by speed to get travel time in hours.
    minutes = hours * 60  # Convert hours into minutes because trip times are easier to read in minutes.
    return max(3, round(minutes))  # Return at least 3 minutes so very short rides still look realistic.


def build_nearby_access_step(location_name, direction_label):  # Create a function that builds a walk or share-auto step near a location.
    distance_meters = get_nearby_walking_distance(location_name)  # Get the sample nearby distance for this location.
    if distance_meters <= MAX_COMFORTABLE_WALK_METERS:  # Check whether the distance is comfortable enough to walk.
        minutes = calculate_walking_time(distance_meters)  # Calculate walking time for this short nearby distance.
        return {  # Return a clean walking step for the app.
            "instruction": f"Walk {distance_meters}m {direction_label} {location_name}",  # Explain the walking instruction in one sentence.
            "mode": "Walk",  # Mark this step as walking.
            "distance_km": round(distance_meters / 1000, 2),  # Store the distance in kilometers for totals.
            "minutes": minutes,  # Store the calculated walking time.
            "fare": 0,  # Walking is free.
            "notes": "Short walking connection.",  # Add a simple beginner-friendly note.
        }  # End the walking step dictionary.

    minutes = calculate_share_auto_time(distance_meters)  # Calculate share-auto time for a longer nearby distance.
    fare = calculate_share_auto_cost(distance_meters)  # Calculate share-auto fare for a longer nearby distance.
    return {  # Return a clean share-auto step for the app.
        "instruction": f"Take share-auto {distance_meters}m {direction_label} {location_name}",  # Explain the share-auto instruction in one sentence.
        "mode": "Share Auto",  # Mark this step as a share-auto ride.
        "distance_km": round(distance_meters / 1000, 2),  # Store the distance in kilometers for totals.
        "minutes": minutes,  # Store the calculated share-auto time.
        "fare": fare,  # Store the calculated share-auto fare.
        "notes": "Estimated share-auto connection for a longer nearby distance.",  # Add a simple beginner-friendly note.
    }  # End the share-auto step dictionary.


def add_nearby_steps(route_output):  # Create a function that adds first-mile and last-mile steps to a route.
    start_step = build_nearby_access_step(route_output["from"], "to the main stop near")  # Build the first-mile step near the start.
    end_step = build_nearby_access_step(route_output["to"], "from the main stop near")  # Build the last-mile step near the destination.
    route_output["steps"] = [start_step] + route_output["steps"] + [end_step]  # Put first-mile, main route, and last-mile steps in order.
    route_output["total_distance_km"] = round(sum(step["distance_km"] for step in route_output["steps"]), 2)  # Add all step distances.
    route_output["total_minutes"] = sum(step["minutes"] for step in route_output["steps"])  # Add all step times.
    route_output["total_fare"] = sum(step["fare"] for step in route_output["steps"])  # Add all step fares.
    return route_output  # Return the updated route with nearby travel included.


def find_direct_route(from_location, to_location):  # Create a function that searches for a direct route only.
    connection = get_connection()  # Open a connection to the database.
    cursor = connection.cursor()  # Create a cursor so we can run a select query.
    cursor.execute(  # Run a SQL query that joins routes with stop names.
        """  -- Start a multi-line SQL select query.
        SELECT routes.mode, routes.distance_km, routes.estimated_minutes, routes.fare_rupees, routes.route_notes  -- Choose the route details to show.
        FROM routes  -- Start from the routes table because we are searching travel routes.
        JOIN stops AS from_stop ON routes.from_stop_id = from_stop.id  -- Join once to find the starting stop name.
        JOIN stops AS to_stop ON routes.to_stop_id = to_stop.id  -- Join again to find the destination stop name.
        WHERE from_stop.name = ? AND to_stop.name = ?  -- Keep only the route matching the user's two dropdown choices.
        """  # End the multi-line SQL select query.
        ,  # Separate the SQL query from the Python values.
        (from_location, to_location),  # Provide the selected From and To locations safely.
    )  # Finish running the route search query.
    route = cursor.fetchone()  # Read the first matching route, or None if no direct route exists.
    connection.close()  # Close the database connection because searching is finished.
    return route  # Return the route row to the Streamlit app.


def find_one_transfer_route(from_location, to_location):  # Create a function that searches for a route with one transfer stop.
    connection = get_connection()  # Open a connection to the SQLite database.
    cursor = connection.cursor()  # Create a cursor so we can run a select query.
    cursor.execute(  # Run a SQL query that connects two route rows through one middle stop.
        """  -- Start a multi-line SQL query for a one-transfer route.
        SELECT  -- Choose all details needed for the two route parts.
            transfer_stop.name AS transfer_stop,  -- Get the stop where the traveler changes route.
            first_route.mode AS first_mode,  -- Get the travel mode for the first part.
            first_route.distance_km AS first_distance_km,  -- Get the distance for the first part.
            first_route.estimated_minutes AS first_minutes,  -- Get the time for the first part.
            first_route.fare_rupees AS first_fare,  -- Get the fare for the first part.
            first_route.route_notes AS first_notes,  -- Get the notes for the first part.
            second_route.mode AS second_mode,  -- Get the travel mode for the second part.
            second_route.distance_km AS second_distance_km,  -- Get the distance for the second part.
            second_route.estimated_minutes AS second_minutes,  -- Get the time for the second part.
            second_route.fare_rupees AS second_fare,  -- Get the fare for the second part.
            second_route.route_notes AS second_notes,  -- Get the notes for the second part.
            first_route.distance_km + second_route.distance_km AS total_distance_km,  -- Add both distances together.
            first_route.estimated_minutes + second_route.estimated_minutes AS total_minutes,  -- Add both travel times together.
            first_route.fare_rupees + second_route.fare_rupees AS total_fare  -- Add both fares together.
        FROM routes AS first_route  -- Start with the first route part.
        JOIN stops AS start_stop ON first_route.from_stop_id = start_stop.id  -- Match the first route to the user's start stop.
        JOIN stops AS transfer_stop ON first_route.to_stop_id = transfer_stop.id  -- Treat the first route destination as the transfer stop.
        JOIN routes AS second_route ON second_route.from_stop_id = transfer_stop.id  -- Find a second route that starts at the transfer stop.
        JOIN stops AS end_stop ON second_route.to_stop_id = end_stop.id  -- Match the second route to the user's final stop.
        WHERE start_stop.name = ? AND end_stop.name = ?  -- Keep only routes from the selected start to the selected destination.
        ORDER BY total_minutes ASC, total_fare ASC  -- Prefer the fastest route, and use lower fare as the tie breaker.
        LIMIT 1  -- Return only the best one-transfer route.
        """  # End the multi-line SQL query.
        ,  # Separate the SQL query from the Python values.
        (from_location, to_location),  # Provide the selected start and destination safely.
    )  # Finish running the one-transfer route search.
    route = cursor.fetchone()  # Read the best matching one-transfer route, or None if no route exists.
    connection.close()  # Close the database connection because searching is finished.
    return route  # Return the one-transfer route row to the caller.


def build_direct_route_output(from_location, to_location, route):  # Create a function that formats a direct route for the app.
    return {  # Return a dictionary so Streamlit can display route details cleanly.
        "route_type": "Direct route",  # Tell the app this route does not need a transfer.
        "from": from_location,  # Store the starting location.
        "to": to_location,  # Store the destination location.
        "total_distance_km": route["distance_km"],  # Store the direct route distance.
        "total_minutes": route["estimated_minutes"],  # Store the direct route travel time.
        "total_fare": route["fare_rupees"],  # Store the direct route fare.
        "steps": [  # Store the trip as a list of simple steps.
            {  # Start the first and only step.
                "instruction": f"Take {route['mode']} from {from_location} to {to_location}",  # Explain the direct travel instruction.
                "from": from_location,  # Store where this step starts.
                "to": to_location,  # Store where this step ends.
                "mode": route["mode"],  # Store the travel mode.
                "distance_km": route["distance_km"],  # Store this step distance.
                "minutes": route["estimated_minutes"],  # Store this step time.
                "fare": route["fare_rupees"],  # Store this step fare.
                "notes": route["route_notes"],  # Store this step travel note.
            }  # End the direct route step.
        ],  # End the steps list.
    }  # End the route output dictionary.


def build_transfer_route_output(from_location, to_location, route):  # Create a function that formats a one-transfer route for the app.
    transfer_stop = route["transfer_stop"]  # Store the transfer stop name in a clear variable.
    return {  # Return a dictionary with the full transfer route details.
        "route_type": "1-transfer route",  # Tell the app this route uses one transfer.
        "from": from_location,  # Store the starting location.
        "to": to_location,  # Store the destination location.
        "transfer_stop": transfer_stop,  # Store the stop where the user changes route.
        "total_distance_km": route["total_distance_km"],  # Store the combined distance.
        "total_minutes": route["total_minutes"],  # Store the combined travel time.
        "total_fare": route["total_fare"],  # Store the combined fare.
        "steps": [  # Store the trip as two clear travel steps.
            {  # Start the first step before the transfer.
                "instruction": f"Take {route['first_mode']} from {from_location} to {transfer_stop}",  # Explain the first travel instruction.
                "from": from_location,  # Store where the first step starts.
                "to": transfer_stop,  # Store where the first step ends.
                "mode": route["first_mode"],  # Store the first step travel mode.
                "distance_km": route["first_distance_km"],  # Store the first step distance.
                "minutes": route["first_minutes"],  # Store the first step time.
                "fare": route["first_fare"],  # Store the first step fare.
                "notes": route["first_notes"],  # Store the first step travel note.
            },  # End the first step.
            {  # Start the second step after the transfer.
                "instruction": f"Take {route['second_mode']} from {transfer_stop} to {to_location}",  # Explain the second travel instruction.
                "from": transfer_stop,  # Store where the second step starts.
                "to": to_location,  # Store where the second step ends.
                "mode": route["second_mode"],  # Store the second step travel mode.
                "distance_km": route["second_distance_km"],  # Store the second step distance.
                "minutes": route["second_minutes"],  # Store the second step time.
                "fare": route["second_fare"],  # Store the second step fare.
                "notes": route["second_notes"],  # Store the second step travel note.
            },  # End the second step.
        ],  # End the steps list.
    }  # End the route output dictionary.


def find_route(from_location, to_location):  # Create the main route-finding function for the Streamlit app.
    direct_route = find_direct_route(from_location, to_location)  # First try to find a route without any transfer.
    if direct_route:  # Check whether a direct route was found.
        route_output = build_direct_route_output(from_location, to_location, direct_route)  # Build a clean direct route result.
        return add_nearby_steps(route_output)  # Add walking or share-auto first-mile and last-mile steps.

    transfer_route = find_one_transfer_route(from_location, to_location)  # If direct route failed, try one transfer.
    if transfer_route:  # Check whether a one-transfer route was found.
        route_output = build_transfer_route_output(from_location, to_location, transfer_route)  # Build a clean one-transfer route result.
        return add_nearby_steps(route_output)  # Add walking or share-auto first-mile and last-mile steps.

    return None  # Return None when no direct or one-transfer route is available.


if __name__ == "__main__":  # Run this block only when database.py is executed directly.
    initialize_database()  # Create the database tables and insert the sample data.
    print("Database created with sample Hyderabad stops and routes.")  # Show a simple success message in the terminal.
