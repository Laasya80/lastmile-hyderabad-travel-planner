import csv  # Import CSV so the app can read real metro fare slabs from a CSV file.

from pathlib import Path  # Import Path so file paths work clearly on Windows and other systems.

import folium  # Import Folium so we can create an interactive OpenStreetMap map.

import pandas as pd  # Import pandas so Streamlit can display analytics tables and charts.

import requests  # Import requests so the app can ask OSRM for real road-route distance.

import streamlit as st  # Import Streamlit so we can build a simple web app.

from difflib import get_close_matches  # Import a simple standard-library tool for fuzzy matching misspelled text.

from math import atan2, cos, radians, sin, sqrt  # Import math helpers for nearby-location distance calculations.

from textwrap import dedent  # Import dedent so indented HTML and CSS strings display correctly.

from streamlit_folium import st_folium  # Import st_folium so Folium maps can be displayed inside Streamlit.

from database import authenticate_user, create_user, find_route, get_all_route_records, get_all_stop_names, get_all_stops_for_map, get_favorite_routes, get_stop_coordinates, get_user_search_history, initialize_database, save_favorite_route, save_user_search  # Import database helper functions for setup, users, route search, analytics, and maps.

METRO_FARE_CSV_PATH = Path("metro_fares.csv")  # Store the metro fare CSV path in one easy-to-change place.

OSRM_ROUTE_BASE_URL = "https://router.project-osrm.org/route/v1"  # Store the public OSRM route API base URL.

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"  # Store the OpenStreetMap Nominatim search API URL.

NOMINATIM_USER_AGENT = "LastMileHyderabadTravelPlanner/1.0"  # Identify this beginner app when calling Nominatim.

HYDERABAD_VIEWBOX = "78.20,17.60,78.75,17.20"  # Limit Nominatim search roughly to Hyderabad using left,top,right,bottom.


def add_custom_css(theme_mode):  # Create a function that adds modern custom styling to the Streamlit page.
    is_dark_mode = theme_mode == "Dark"  # Check whether the user selected dark mode.
    app_background = "#0f172a" if is_dark_mode else "#f4f7fb"  # Choose the main page background color.
    card_background = "#162033" if is_dark_mode else "#ffffff"  # Choose the card background color.
    panel_background = "#111827" if is_dark_mode else "#eef6ff"  # Choose the search and hero panel background.
    text_color = "#e5edf7" if is_dark_mode else "#172033"  # Choose the main text color.
    muted_text = "#aab8c9" if is_dark_mode else "#5b6b7d"  # Choose the secondary text color.
    border_color = "#2b3a52" if is_dark_mode else "#dbe5ef"  # Choose the border color.
    sidebar_background = "#0b1220" if is_dark_mode else "#102a43"  # Choose the sidebar background color.
    st.markdown(  # Add CSS using Streamlit markdown.
        dedent(  # Remove Python indentation from the CSS before sending it to Streamlit.
            f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        .stApp {{
            background: {app_background};
            color: {text_color};
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}

        .block-container {{
            max-width: 1180px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3 {{
            color: {text_color};
            font-weight: 800;
            letter-spacing: 0;
        }}

        .stMarkdown, .stCaption, label, [data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"] p {{
            color: {text_color};
        }}

        [data-testid="stCaptionContainer"], .stCaption {{
            color: {muted_text};
        }}

        .hero-box, .section-card, .route-card, .metric-card, .step-card, .compare-card {{
            border-radius: 8px;
        }}

        .hero-box {{
            background: {panel_background};
            border: 1px solid {border_color};
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
            margin-bottom: 1rem;
            padding: 1.4rem;
        }}

        .hero-title {{
            color: {text_color};
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.15;
            margin: 0 0 0.5rem 0;
        }}

        .hero-subtitle {{
            color: {muted_text};
            font-size: 1rem;
            margin: 0;
        }}

        .section-card, .route-card {{
            background: {card_background};
            border: 1px solid {border_color};
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.10);
            margin: 1rem 0;
            padding: 1.1rem;
        }}

        .route-title-row {{
            align-items: center;
            display: flex;
            gap: 0.8rem;
            justify-content: space-between;
            margin-bottom: 0.9rem;
        }}

        .route-title {{
            color: {text_color};
            font-size: 1.18rem;
            font-weight: 800;
            line-height: 1.25;
        }}

        .route-pill {{
            background: rgba(20, 184, 166, 0.14);
            border: 1px solid rgba(20, 184, 166, 0.28);
            border-radius: 999px;
            color: {text_color};
            font-size: 0.8rem;
            font-weight: 800;
            padding: 0.28rem 0.7rem;
            white-space: nowrap;
        }}

        .metric-card {{
            background: {card_background};
            border: 1px solid {border_color};
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
            min-height: 112px;
            padding: 1rem;
        }}

        .metric-label {{
            color: {muted_text};
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0;
            margin-bottom: 0.35rem;
            text-transform: uppercase;
        }}

        .metric-value {{
            color: {text_color};
            font-size: 1.28rem;
            font-weight: 800;
            line-height: 1.25;
        }}

        .step-card, .compare-card {{
            background: {card_background};
            border: 1px solid {border_color};
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.09);
            margin-bottom: 0.8rem;
            padding: 1rem;
        }}

        .step-title, .compare-title {{
            color: {text_color};
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }}

        .step-meta, .step-note, .compare-meta {{
            color: {muted_text};
            font-size: 0.9rem;
        }}

        .badge-row, .badge-stack {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0.5rem 0 0.7rem 0;
        }}

        .transport-badge {{
            background: rgba(37, 99, 235, 0.10);
            border: 1px solid rgba(37, 99, 235, 0.22);
            border-radius: 999px;
            color: {text_color};
            display: inline-block;
            font-size: 0.8rem;
            font-weight: 800;
            padding: 0.25rem 0.65rem;
        }}

        .history-item {{
            background: {card_background};
            border: 1px solid {border_color};
            border-radius: 8px;
            color: {text_color};
            margin-bottom: 0.5rem;
            padding: 0.65rem 0.8rem;
        }}

        .suggestion-pill {{
            background: #fff7ed;
            border: 1px solid #fed7aa;
            border-radius: 999px;
            color: #9a4b00;
            display: inline-block;
            font-size: 0.85rem;
            font-weight: 700;
            margin: 0.2rem 0.25rem 0.2rem 0;
            padding: 0.3rem 0.7rem;
        }}

        .compare-card {{
            min-height: 230px;
        }}

        .compare-card-highlight {{
            border-color: #38bdf8;
            box-shadow: 0 16px 34px rgba(14, 165, 233, 0.16);
        }}

        .compare-header {{
            align-items: center;
            display: flex;
            gap: 0.7rem;
            margin-bottom: 0.75rem;
        }}

        .transport-icon {{
            align-items: center;
            background: #2563eb;
            border-radius: 8px;
            color: #ffffff;
            display: inline-flex;
            flex: 0 0 2.4rem;
            font-size: 0.95rem;
            font-weight: 800;
            height: 2.4rem;
            justify-content: center;
            width: 2.4rem;
        }}

        .transport-icon-metro {{ background: #7c3aed; }}
        .transport-icon-bike {{ background: #0891b2; }}
        .transport-icon-auto {{ background: #f59e0b; color: #111827; }}
        .transport-icon-car {{ background: #2563eb; }}
        .transport-icon-bus {{ background: #16a34a; }}
        .transport-icon-walk {{ background: #64748b; }}

        .compare-grid {{
            display: grid;
            gap: 0.45rem;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            margin-top: 0.75rem;
        }}

        .compare-stat {{
            background: rgba(148, 163, 184, 0.10);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 8px;
            padding: 0.55rem;
        }}

        .compare-stat-label {{
            color: {muted_text};
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
        }}

        .compare-stat-value {{
            color: {text_color};
            font-size: 0.95rem;
            font-weight: 800;
            margin-top: 0.1rem;
        }}

        .winner-label {{
            background: #2563eb;
            border-radius: 999px;
            color: #ffffff;
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 800;
            padding: 0.24rem 0.62rem;
        }}

        .winner-label-cheapest {{ background: #16a34a; }}
        .winner-label-fastest {{ background: #dc2626; }}
        .winner-label-preference {{ background: #7c3aed; }}
        .winner-label-budget {{ background: #f59e0b; color: #111827; }}

        .loading-strip {{
            animation: pulseRoute 1.2s ease-in-out infinite;
            background: linear-gradient(90deg, #2563eb, #14b8a6, #f59e0b);
            border-radius: 999px;
            height: 0.35rem;
            margin: 0.8rem 0;
        }}

        @keyframes pulseRoute {{
            0% {{ opacity: 0.45; transform: scaleX(0.94); }}
            50% {{ opacity: 1; transform: scaleX(1); }}
            100% {{ opacity: 0.45; transform: scaleX(0.94); }}
        }}

        div[data-testid="stDataFrame"] {{
            background: {card_background};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 0.35rem;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
        }}

        .stButton > button {{
            background: #2563eb;
            border: 1px solid #2563eb;
            border-radius: 8px;
            color: #ffffff;
            font-weight: 800;
            min-height: 2.8rem;
            width: 100%;
        }}

        .stButton > button * {{
            color: #ffffff !important;
        }}

        .stButton > button:hover {{
            background: #1d4ed8;
            border-color: #1d4ed8;
            color: #ffffff;
        }}

        [data-testid="stSidebar"] {{
            background: {sidebar_background};
        }}

        [data-testid="stSidebar"] * {{
            color: #f8fafc;
        }}

        @media (max-width: 700px) {{
            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }}

            .hero-title {{
                font-size: 1.65rem;
            }}

            .metric-card {{
                min-height: auto;
            }}

            .compare-grid {{
                grid-template-columns: 1fr;
            }}

            .route-title-row {{
                align-items: flex-start;
                flex-direction: column;
            }}
        }}
        </style>
        """,  # End the multi-line CSS block.
        ),  # Finish removing extra indentation from the CSS string.
        unsafe_allow_html=True,  # Allow Streamlit to render the CSS styles.
    )  # Finish adding custom CSS.


def show_sidebar():  # Create a function that displays project information in the sidebar.
    with st.sidebar:  # Put all sidebar content inside Streamlit's sidebar.
        st.title("LastMile")  # Show the short project name in the sidebar.
        st.write("Hyderabad local travel planner for metro, bus, walking, and share-auto connections.")  # Explain what the app does.
        st.markdown("---")  # Add a visual divider.
        st.write("Built with:")  # Introduce the project tools.
        st.write("Python")  # Show Python as the programming language.
        st.write("Streamlit")  # Show Streamlit as the app framework.
        st.write("SQLite")  # Show SQLite as the database.
        st.write("Folium + OpenStreetMap")  # Show Folium and OpenStreetMap as the map tools.
        st.write("Nominatim location search")  # Show Nominatim as the real-place search tool.
        st.markdown("---")  # Add another visual divider.
        show_authentication_panel()  # Show signup, login, logout, and account controls.
        st.markdown("---")  # Add a divider after the account panel.
        st.write("Sample coverage: 15 Hyderabad stops and realistic sample routes.")  # Show a short data note.
        if "search_history" in st.session_state and st.session_state["search_history"]:  # Check whether there are saved searches.
            st.markdown("---")  # Add a divider before history.
            st.subheader("Search History")  # Show a small heading for search history.
            for history_item in st.session_state["search_history"][-5:][::-1]:  # Show the latest five searches first.
                st.markdown(f"<div class='history-item'>{history_item}</div>", unsafe_allow_html=True)  # Display one history item.


def setup_session_state():  # Create a function that prepares Streamlit session values.
    if "search_history" not in st.session_state:  # Check whether search history has been created yet.
        st.session_state["search_history"] = []  # Create an empty search history list.
    if "route_search_counts" not in st.session_state:  # Check whether route search counts have been created yet.
        st.session_state["route_search_counts"] = {}  # Create a dictionary that stores how many times each route is searched.
    if "from_choice" not in st.session_state:  # Check whether the From dropdown value has been saved yet.
        st.session_state["from_choice"] = "Ameerpet"  # Use Ameerpet as the default starting point.
    if "to_choice" not in st.session_state:  # Check whether the To dropdown value has been saved yet.
        st.session_state["to_choice"] = "Hitech City"  # Use Hitech City as the default destination.
    if "current_route" not in st.session_state:  # Check whether a route result has been saved yet.
        st.session_state["current_route"] = None  # Start with no saved route result.
    if "current_from_location" not in st.session_state:  # Check whether a saved From result exists yet.
        st.session_state["current_from_location"] = None  # Start with no saved From result.
    if "current_to_location" not in st.session_state:  # Check whether a saved To result exists yet.
        st.session_state["current_to_location"] = None  # Start with no saved To result.
    if "travel_preference" not in st.session_state:  # Check whether the user preference has been saved yet.
        st.session_state["travel_preference"] = "Cheapest"  # Use Cheapest as the default recommendation style.
    if "budget_limit" not in st.session_state:  # Check whether the budget limit has been saved yet.
        st.session_state["budget_limit"] = 0  # Use zero to mean no budget limit.
    if "theme_mode" not in st.session_state:  # Check whether the UI theme has been saved yet.
        st.session_state["theme_mode"] = "Light"  # Use light mode as the default theme.
    if "logged_in_user" not in st.session_state:  # Check whether a logged-in user has been saved yet.
        st.session_state["logged_in_user"] = None  # Start with no logged-in user.
    if "auth_message" not in st.session_state:  # Check whether an authentication message exists yet.
        st.session_state["auth_message"] = ""  # Start with no login or signup message.


def set_popular_route(from_location, to_location):  # Create a function that fills the search form from a popular route.
    st.session_state["from_choice"] = from_location  # Save the popular route starting point.
    st.session_state["to_choice"] = to_location  # Save the popular route destination.


def get_logged_in_user():  # Create a function that returns the current logged-in user.
    return st.session_state.get("logged_in_user")  # Read the logged-in user dictionary from session state.


def is_user_logged_in():  # Create a function that checks whether someone is logged in.
    return get_logged_in_user() is not None  # Return True when a user dictionary exists.


def load_logged_in_user_history():  # Create a function that loads database search history for the logged-in user.
    user = get_logged_in_user()  # Read the current user.
    if not user:  # Check whether nobody is logged in.
        return  # Stop because there is no user history to load.
    history_rows = get_user_search_history(user["id"])  # Read recent saved searches from SQLite.
    history_labels = [f"{row['from_location']} to {row['to_location']}" for row in history_rows]  # Convert database rows into labels.
    st.session_state["search_history"] = history_labels[::-1]  # Store oldest-to-newest labels so the sidebar can reverse them.
    search_counts = {}  # Create a dictionary for analytics counts.
    for row in get_user_search_history(user["id"], limit=100):  # Read more rows for count analytics.
        route_label = f"{row['from_location']} to {row['to_location']}"  # Build a route label.
        search_counts[route_label] = search_counts.get(route_label, 0) + 1  # Count how many times this user searched it.
    st.session_state["route_search_counts"] = search_counts  # Save counts for the analytics dashboard.


def show_authentication_panel():  # Create a function that displays signup, login, and logout controls.
    st.sidebar.subheader("Account")  # Show the account section heading.
    user = get_logged_in_user()  # Read the current logged-in user.
    if user:  # Check whether a user is logged in.
        st.sidebar.success(f"Logged in as {user['username']}")  # Show the logged-in username.
        if st.sidebar.button("Logout"):  # Create a logout button.
            st.session_state["logged_in_user"] = None  # Clear the logged-in user.
            st.session_state["search_history"] = []  # Clear user search history from this session.
            st.session_state["route_search_counts"] = {}  # Clear user analytics counts from this session.
            st.session_state["auth_message"] = "Logged out."  # Store a short logout message.
            st.rerun()  # Rerun so the UI updates immediately.
        return  # Stop because logged-in users do not need login forms.
    auth_tab, signup_tab = st.sidebar.tabs(["Login", "Signup"])  # Create sidebar tabs for login and signup.
    with auth_tab:  # Put login controls in the Login tab.
        login_username = st.text_input("Login username", key="login_username")  # Let the user type a username.
        login_password = st.text_input("Login password", type="password", key="login_password")  # Let the user type a hidden password.
        if st.button("Login"):  # Create the login button.
            user_data = authenticate_user(login_username, login_password)  # Check the username and password.
            if user_data:  # Check whether login worked.
                st.session_state["logged_in_user"] = user_data  # Save the user in session state.
                st.session_state["auth_message"] = "Login successful."  # Store a success message.
                load_logged_in_user_history()  # Load this user's saved history.
                st.rerun()  # Rerun so the logged-in UI appears.
            else:  # Run this block when login failed.
                st.session_state["auth_message"] = "Invalid username or password."  # Store an error message.
    with signup_tab:  # Put signup controls in the Signup tab.
        signup_username = st.text_input("Signup username", key="signup_username")  # Let the user choose a username.
        signup_password = st.text_input("Signup password", type="password", key="signup_password")  # Let the user choose a hidden password.
        if st.button("Create Account"):  # Create the signup button.
            success, message = create_user(signup_username, signup_password)  # Try creating the user in SQLite.
            st.session_state["auth_message"] = message  # Store the signup result message.
            if success:  # Check whether signup worked.
                st.sidebar.success(message)  # Show success immediately.
            else:  # Run this block when signup failed.
                st.sidebar.error(message)  # Show the validation error immediately.
    if st.session_state["auth_message"]:  # Check whether there is an auth message to show.
        st.sidebar.caption(st.session_state["auth_message"])  # Show the latest auth message.


def show_favorite_routes_panel():  # Create a function that displays saved favorite routes.
    user = get_logged_in_user()  # Read the logged-in user.
    if not user:  # Check whether nobody is logged in.
        return  # Stop because favorites only exist for logged-in users.
    favorite_routes = get_favorite_routes(user["id"])  # Read favorites from SQLite.
    st.subheader("Favorite Routes")  # Show the favorite routes heading.
    if not favorite_routes:  # Check whether this user has no favorites yet.
        st.caption("Save a route after searching to see it here.")  # Explain how to add favorites.
        return  # Stop because there are no favorite buttons to show.
    favorite_columns = st.columns(min(3, len(favorite_routes)))  # Create a compact row of favorite buttons.
    for index, favorite in enumerate(favorite_routes[:6]):  # Show up to six recent favorites.
        route_label = f"{favorite['from_location']} to {favorite['to_location']}"  # Build a readable favorite label.
        with favorite_columns[index % len(favorite_columns)]:  # Place the favorite button in a column.
            if st.button(route_label, key=f"favorite_{index}_{route_label}"):  # Create a button for this favorite route.
                set_popular_route(favorite["from_location"], favorite["to_location"])  # Fill the route form with this favorite.
                st.rerun()  # Rerun the app so the dropdowns update.


def show_save_favorite_button(from_location, to_location):  # Create a function that saves the current route as a favorite.
    user = get_logged_in_user()  # Read the logged-in user.
    if not user:  # Check whether nobody is logged in.
        st.caption("Log in to save this route as a favorite.")  # Tell guests how to use favorites.
        return  # Stop because guests cannot save favorites.
    if st.button("Save Favorite Route"):  # Show a button for saving the current route.
        success, message = save_favorite_route(user["id"], from_location, to_location)  # Save the favorite in SQLite.
        if success:  # Check whether the route was newly saved.
            st.success(message)  # Show success feedback.
        else:  # Run this block when the route was already saved.
            st.info(message)  # Show a friendly duplicate message.


def find_location_match(user_text, locations):  # Create a function that handles exact and fuzzy location matching.
    cleaned_text = user_text.strip()  # Remove extra spaces from what the user typed.
    if not cleaned_text:  # Check whether the user left the text field blank.
        return None, []  # Return no match and no suggestions.
    lowercase_locations = {location.lower(): location for location in locations}  # Create a lowercase lookup for exact matching.
    if cleaned_text.lower() in lowercase_locations:  # Check for an exact match while ignoring letter case.
        return lowercase_locations[cleaned_text.lower()], []  # Return the correctly capitalized location name.
    close_matches = get_close_matches(cleaned_text, locations, n=3, cutoff=0.55)  # Find up to three similar location names.
    if close_matches:  # Check whether fuzzy matching found anything useful.
        return close_matches[0], close_matches  # Use the closest match and return all suggestions.
    return None, []  # Return no match when the typed text is too different.


@st.cache_data(ttl=3600)  # Cache Nominatim results for one hour so repeated typing does not call the API too often.
def search_nominatim_locations(search_text):  # Create a function that searches real Hyderabad places using OpenStreetMap Nominatim.
    cleaned_text = search_text.strip()  # Remove extra spaces from the user's search text.
    if len(cleaned_text) < 3:  # Avoid calling the API for very short text.
        return []  # Return no suggestions until the user has typed enough.
    query_text = f"{cleaned_text}, Hyderabad, Telangana, India"  # Add city context so Nominatim searches Hyderabad first.
    params = {  # Create the query parameters sent to the Nominatim API.
        "q": query_text,  # Tell Nominatim what place name to search for.
        "format": "json",  # Ask Nominatim to return JSON because Python can read it easily.
        "addressdetails": 1,  # Ask for address details so suggestions are easier to understand.
        "limit": 5,  # Ask for only five suggestions to keep the UI simple.
        "countrycodes": "in",  # Limit results to India.
        "viewbox": HYDERABAD_VIEWBOX,  # Bias and bound results to the Hyderabad area.
        "bounded": 1,  # Force Nominatim to stay inside the Hyderabad viewbox.
    }  # End the Nominatim query parameters.
    headers = {"User-Agent": NOMINATIM_USER_AGENT}  # Send a User-Agent because Nominatim requires apps to identify themselves.
    try:  # Try the API request because internet or API availability can fail.
        response = requests.get(NOMINATIM_SEARCH_URL, params=params, headers=headers, timeout=6)  # Call Nominatim with the search parameters.
        response.raise_for_status()  # Stop if the API returns an HTTP error.
        results = response.json()  # Convert the JSON response into Python data.
    except (requests.RequestException, ValueError):  # Handle network errors and invalid JSON.
        return []  # Return no suggestions if the API call fails.
    suggestions = []  # Create an empty list for cleaned suggestions.
    for result in results:  # Loop through every Nominatim result.
        suggestions.append(  # Add one suggestion dictionary.
            {  # Start the suggestion dictionary.
                "label": result.get("display_name", "Unknown place"),  # Store the full place label for autocomplete.
                "latitude": float(result["lat"]),  # Store the latitude as a number.
                "longitude": float(result["lon"]),  # Store the longitude as a number.
            }  # End the suggestion dictionary.
        )  # Finish adding this suggestion.
    return suggestions  # Return the cleaned list of Nominatim suggestions.


def build_suggestion_labels(suggestions):  # Create a function that converts suggestion dictionaries into selectbox labels.
    labels = []  # Create an empty list for labels.
    for index, suggestion in enumerate(suggestions, start=1):  # Loop through suggestions with a visible number.
        labels.append(f"{index}. {suggestion['label']}")  # Add a numbered label for the autocomplete selectbox.
    return labels  # Return the list of labels.


def get_selected_suggestion(selected_label, suggestions):  # Create a function that finds the suggestion chosen in the selectbox.
    labels = build_suggestion_labels(suggestions)  # Rebuild labels in the same order as the selectbox.
    if selected_label in labels:  # Check whether the user selected a real label.
        selected_index = labels.index(selected_label)  # Find the selected label position.
        return suggestions[selected_index]  # Return the matching suggestion dictionary.
    return None  # Return nothing if there is no selected suggestion.


def find_nearest_known_stop(latitude, longitude, locations):  # Create a function that maps any real place to the nearest sample stop.
    real_point = (latitude, longitude)  # Store the real searched place as a coordinate pair.
    nearest_location = None  # Start with no nearest location.
    nearest_distance = None  # Start with no nearest distance.
    for location in locations:  # Loop through every known LastMile stop.
        stop_coordinates = get_stop_coordinates(location)  # Get coordinates for this known stop.
        if stop_coordinates:  # Only compare stops that have coordinates.
            distance = calculate_distance_between_coordinates(real_point, stop_coordinates)  # Calculate distance from the real place to this stop.
            if nearest_distance is None or distance < nearest_distance:  # Check whether this is the closest stop so far.
                nearest_location = location  # Save this stop as the nearest location.
                nearest_distance = distance  # Save this distance as the nearest distance.
    return nearest_location, round(nearest_distance, 2) if nearest_distance is not None else None  # Return the nearest stop and distance.


def resolve_location_for_route(dropdown_location, typed_location, selected_suggestion, locations):  # Create a function that resolves dropdown or real typed place into a route stop.
    if selected_suggestion:  # Check whether the user selected a real Nominatim suggestion.
        nearest_stop, nearest_distance = find_nearest_known_stop(selected_suggestion["latitude"], selected_suggestion["longitude"], locations)  # Find the closest sample stop.
        return {  # Return a clean resolved-location dictionary.
            "route_location": nearest_stop,  # Store the known stop used for the route engine.
            "display_name": selected_suggestion["label"],  # Store the real place name shown to the user.
            "latitude": selected_suggestion["latitude"],  # Store the real latitude.
            "longitude": selected_suggestion["longitude"],  # Store the real longitude.
            "nearest_distance": nearest_distance,  # Store how far the real place is from the known stop.
            "source": "Nominatim",  # Mark this location as coming from OpenStreetMap Nominatim.
        }  # End the resolved real-location dictionary.
    matched_location, suggestions = find_location_match(typed_location, locations) if typed_location else (dropdown_location, [])  # Use fuzzy matching or dropdown value.
    if matched_location:  # Check whether a known stop was found.
        coordinates = get_stop_coordinates(matched_location)  # Get coordinates for the matched known stop.
        return {  # Return a clean resolved known-stop dictionary.
            "route_location": matched_location,  # Store the known stop used for routing.
            "display_name": matched_location,  # Store the display name.
            "latitude": coordinates[0] if coordinates else None,  # Store latitude when available.
            "longitude": coordinates[1] if coordinates else None,  # Store longitude when available.
            "nearest_distance": 0,  # Known stops are zero km from themselves.
            "source": "Local sample stop",  # Mark this location as local sample data.
        }  # End the resolved known-stop dictionary.
    return {"route_location": None, "suggestions": suggestions, "source": "Invalid"}  # Return invalid status when nothing matches.


def calculate_distance_between_coordinates(first_point, second_point):  # Create a function that estimates distance between two map points.
    earth_radius_km = 6371  # Store Earth's radius in kilometers for the distance formula.
    first_latitude = radians(first_point[0])  # Convert the first latitude from degrees to radians.
    second_latitude = radians(second_point[0])  # Convert the second latitude from degrees to radians.
    latitude_change = radians(second_point[0] - first_point[0])  # Calculate latitude difference in radians.
    longitude_change = radians(second_point[1] - first_point[1])  # Calculate longitude difference in radians.
    formula_part = sin(latitude_change / 2) ** 2 + cos(first_latitude) * cos(second_latitude) * sin(longitude_change / 2) ** 2  # Calculate the main Haversine value.
    angle = 2 * atan2(sqrt(formula_part), sqrt(1 - formula_part))  # Convert the Haversine value into an angle.
    return earth_radius_km * angle  # Return the approximate distance in kilometers.


def get_nearby_locations(location_name, locations):  # Create a function that suggests nearby Hyderabad locations.
    start_coordinates = get_stop_coordinates(location_name)  # Get coordinates for the selected location.
    if not start_coordinates:  # Check whether the selected location has coordinates.
        return []  # Return no nearby suggestions if coordinates are missing.
    nearby_locations = []  # Create an empty list for nearby location suggestions.
    for other_location in locations:  # Loop through every known location.
        if other_location != location_name:  # Skip the selected location itself.
            other_coordinates = get_stop_coordinates(other_location)  # Get coordinates for the possible nearby location.
            if other_coordinates:  # Only use locations that have coordinates.
                distance = calculate_distance_between_coordinates(start_coordinates, other_coordinates)  # Calculate approximate distance.
                nearby_locations.append((other_location, distance))  # Save the location and its distance.
    nearby_locations.sort(key=lambda item: item[1])  # Sort suggestions by shortest distance first.
    return nearby_locations[:3]  # Return the three nearest locations.


def estimate_traffic_delay(route):  # Create a function that estimates extra traffic delay for the route.
    delay_minutes = 0  # Start with zero delay.
    for step in route["steps"]:  # Loop through every route step.
        mode = step["mode"].lower()  # Convert the transport mode to lowercase for easier checking.
        if "metro" in mode or "walk" in mode:  # Metro and walking are usually less affected by road traffic.
            delay_minutes += 0  # Add no extra delay for metro or walking.
        elif "share auto" in mode or "auto" in mode:  # Autos can be delayed in city traffic.
            delay_minutes += max(2, round(step["minutes"] * 0.2))  # Add about 20 percent delay, with at least 2 minutes.
        else:  # Buses and cabs can face heavier road traffic.
            delay_minutes += max(3, round(step["minutes"] * 0.25))  # Add about 25 percent delay, with at least 3 minutes.
    return delay_minutes  # Return the total estimated traffic delay.


def add_search_history(from_location, to_location):  # Create a function that saves a successful search in session history.
    history_text = f"{from_location} to {to_location}"  # Build a readable history label.
    current_count = st.session_state["route_search_counts"].get(history_text, 0)  # Read the current search count for this route.
    st.session_state["route_search_counts"][history_text] = current_count + 1  # Increase the route search count by one.
    user = get_logged_in_user()  # Read the current logged-in user.
    if user:  # Check whether the user is logged in.
        save_user_search(user["id"], from_location, to_location)  # Save this search permanently in SQLite.
    if history_text in st.session_state["search_history"]:  # Check whether this route is already in history.
        st.session_state["search_history"].remove(history_text)  # Remove the old copy so the new copy can move to the top.
    st.session_state["search_history"].append(history_text)  # Add the latest search to the end of the list.
    st.session_state["search_history"] = st.session_state["search_history"][-8:]  # Keep only the latest eight searches.


def get_transport_badges(route):  # Create a function that finds unique transport types for badge display.
    badges = []  # Create an empty list for transport badges.
    for step in route["steps"]:  # Loop through each route step.
        if step["mode"] not in badges:  # Check whether this mode has already been added.
            badges.append(step["mode"])  # Add the new transport mode.
    return badges  # Return the unique transport modes in route order.


def show_transport_badges(route):  # Create a function that displays transport type badges.
    badge_html = "<div class='badge-row'>"  # Start a badge row.
    for badge in get_transport_badges(route):  # Loop through each transport badge.
        icon_label, _icon_class = get_transport_icon_details(badge)  # Get a short transport icon label.
        badge_html += f"<span class='transport-badge'>{icon_label} {badge}</span>"  # Add one badge with an icon label to the HTML.
    badge_html += "</div>"  # End the badge row.
    st.markdown(badge_html, unsafe_allow_html=True)  # Display the badges in Streamlit.


def show_nearby_locations(title, location_name, locations):  # Create a function that displays nearby location suggestions.
    nearby_locations = get_nearby_locations(location_name, locations)  # Get nearby locations for the selected stop.
    if nearby_locations:  # Check whether suggestions exist.
        st.caption(title)  # Show a short label above the suggestions.
        nearby_html = ""  # Create an empty HTML string.
        for nearby_name, distance in nearby_locations:  # Loop through each nearby suggestion.
            nearby_html += f"<span class='suggestion-pill'>{nearby_name} - {distance:.1f} km</span>"  # Add one suggestion pill.
        st.markdown(nearby_html, unsafe_allow_html=True)  # Display the nearby suggestion pills.


def build_search_analytics_dataframe():  # Create a function that turns search counts into chart data.
    rows = []  # Create an empty list for search analytics rows.
    for route_label, search_count in st.session_state["route_search_counts"].items():  # Loop through every searched route and its count.
        rows.append({"Route": route_label, "Searches": search_count})  # Add one readable row for the chart.
    if not rows:  # Check whether the user has not searched anything yet.
        return pd.DataFrame([{"Route": "No searches yet", "Searches": 0}])  # Return one placeholder row so the chart area is not empty.
    search_dataframe = pd.DataFrame(rows)  # Convert the rows into a pandas DataFrame.
    return search_dataframe.sort_values("Searches", ascending=False).head(8)  # Return the most searched routes first.


def build_route_analytics_dataframe():  # Create a function that reads route data for analytics.
    route_records = get_all_route_records()  # Read all sample route records from SQLite.
    return pd.DataFrame(route_records)  # Convert route dictionaries into a pandas DataFrame for charts.


def build_mode_analytics_dataframe(route_dataframe):  # Create a function that counts popular transport modes.
    mode_rows = []  # Create an empty list for mode count rows.
    for mode_text in route_dataframe["mode"]:  # Loop through every route mode from the database.
        for mode_part in mode_text.replace("/", ",").split(","):  # Split mixed modes like Bus/Auto into separate mode names.
            clean_mode = mode_part.strip()  # Remove extra spaces around the mode name.
            if clean_mode:  # Check whether the cleaned mode is not empty.
                mode_rows.append(clean_mode)  # Add this mode to the counting list.
    mode_dataframe = pd.DataFrame({"Mode": mode_rows})  # Convert the mode list into a DataFrame.
    return mode_dataframe["Mode"].value_counts().reset_index(name="Routes").rename(columns={"index": "Mode"})  # Count routes per mode.


def build_cheapest_routes_dataframe(route_dataframe):  # Create a function that finds the cheapest sample routes.
    cheapest_dataframe = route_dataframe.copy()  # Copy the route data so the original DataFrame is not changed.
    cheapest_dataframe["Route"] = cheapest_dataframe["from_location"] + " to " + cheapest_dataframe["to_location"]  # Build readable route labels.
    cheapest_dataframe = cheapest_dataframe.sort_values(["fare_rupees", "estimated_minutes"], ascending=True).head(8)  # Keep the lowest fare routes.
    return cheapest_dataframe[["Route", "mode", "fare_rupees", "estimated_minutes"]]  # Return only the columns needed for display.


def show_analytics_dashboard():  # Create a function that displays the analytics dashboard.
    route_dataframe = build_route_analytics_dataframe()  # Build route data from SQLite.
    search_dataframe = build_search_analytics_dataframe()  # Build search count data from session state.
    mode_dataframe = build_mode_analytics_dataframe(route_dataframe)  # Build popular transport mode data.
    cheapest_dataframe = build_cheapest_routes_dataframe(route_dataframe)  # Build cheapest route data.
    average_cost = round(route_dataframe["fare_rupees"].mean())  # Calculate average fare across sample routes.
    average_time = round(route_dataframe["estimated_minutes"].mean())  # Calculate average travel time across sample routes.
    dashboard_tab, charts_tab = st.tabs(["Analytics Overview", "Charts and Tables"])  # Create two simple dashboard tabs.
    with dashboard_tab:  # Put high-level dashboard cards in the first tab.
        st.subheader("Analytics Dashboard")  # Show the dashboard heading.
        metric_columns = st.columns(4)  # Create four KPI columns.
        with metric_columns[0]:  # Use the first KPI column for searched routes.
            show_metric_card("Tracked Searches", sum(st.session_state["route_search_counts"].values()))  # Show total searches in this session.
        with metric_columns[1]:  # Use the second KPI column for average cost.
            show_metric_card("Average Trip Cost", f"Rs. {average_cost}")  # Show average fare.
        with metric_columns[2]:  # Use the third KPI column for average time.
            show_metric_card("Average Travel Time", f"{average_time} mins")  # Show average time.
        with metric_columns[3]:  # Use the fourth KPI column for sample routes.
            show_metric_card("Sample Routes", len(route_dataframe))  # Show the number of route records.
        chart_columns = st.columns(2)  # Create two chart columns.
        with chart_columns[0]:  # Put search chart in the first column.
            st.write("Most Searched Routes")  # Label the chart.
            st.bar_chart(search_dataframe.set_index("Route"))  # Draw a bar chart for route searches.
        with chart_columns[1]:  # Put mode chart in the second column.
            st.write("Popular Transport Modes")  # Label the chart.
            st.bar_chart(mode_dataframe.set_index("Mode"))  # Draw a bar chart for transport mode popularity.
    with charts_tab:  # Put detailed charts and tables in the second tab.
        st.subheader("Cheapest Routes in Hyderabad")  # Show the cheapest routes heading.
        st.bar_chart(cheapest_dataframe.set_index("Route")["fare_rupees"])  # Draw a fare bar chart for cheapest routes.
        st.dataframe(cheapest_dataframe, use_container_width=True, hide_index=True)  # Show the cheapest route table.
        st.subheader("Route Data Summary")  # Show a heading for raw summary data.
        st.dataframe(route_dataframe, use_container_width=True, hide_index=True)  # Show the full route analytics data.


def get_walking_distance_from_route(route):  # Create a function that adds walking distance from all walking steps.
    walking_distance = 0  # Start with zero walking distance.
    for step in route["steps"]:  # Loop through every route step.
        if step["mode"] == "Walk":  # Check whether the step is a walking step.
            walking_distance += step["distance_km"]  # Add this walking distance to the total.
    return round(walking_distance, 2)  # Return a clean walking distance in kilometers.


def calculate_ride_cost(base_fare, per_km_fare, distance_km):  # Create a function that calculates fare from a base price and per-km price.
    estimated_cost = base_fare + (per_km_fare * distance_km)  # Add the base fare to the distance-based fare.
    return round(estimated_cost)  # Round the fare so users see a simple rupee amount.


def calculate_ride_time(distance_km, speed_km_per_hour):  # Create a function that estimates travel time from distance and speed.
    hours = distance_km / speed_km_per_hour  # Divide distance by speed to get time in hours.
    minutes = hours * 60  # Convert hours into minutes.
    return max(5, round(minutes))  # Return at least 5 minutes so very short rides look realistic.


def get_main_route_distance(route):  # Create a function that finds the main trip distance without walking access steps.
    road_distance = 0  # Start with zero distance.
    for step in route["steps"]:  # Loop through each route step.
        if step["mode"] != "Walk":  # Skip walking steps because ride apps usually cover the main road distance.
            road_distance += step["distance_km"]  # Add non-walking distance to the road distance.
    if road_distance == 0:  # Check whether every step was walking.
        return route["total_distance_km"]  # Use the full route distance as a fallback.
    return round(road_distance, 2)  # Return the main road distance.


def has_metro_step(route):  # Create a function that checks whether the route includes metro travel.
    for step in route["steps"]:  # Loop through every route step.
        if "Metro" in step["mode"]:  # Check whether the step mode contains Metro.
            return True  # Return True as soon as a metro step is found.
    return False  # Return False when there is no metro step.


def get_location_pair_from_route(route):  # Create a function that reads the start and end locations from a route.
    return route["from"], route["to"]  # Return the route start and destination names.


def estimate_fallback_route(from_coordinates, to_coordinates, profile):  # Create a function that estimates distance and time when OSRM is unavailable.
    straight_line_km = calculate_distance_between_coordinates(from_coordinates, to_coordinates)  # Calculate direct map distance between points.
    multiplier = 1.15 if profile == "walking" else 1.25  # Walking paths are closer to straight-line than road driving routes.
    estimated_distance = straight_line_km * multiplier  # Estimate route distance from direct distance.
    fallback_speed = 5 if profile == "walking" else 22  # Use 5 km/h for walking and 22 km/h for city driving.
    estimated_minutes = calculate_ride_time(estimated_distance, fallback_speed)  # Estimate time from fallback distance and speed.
    return round(estimated_distance, 2), estimated_minutes, "Estimated"  # Return fallback distance, time, and source type.


def get_osrm_route_from_coordinates(from_coordinates, to_coordinates, profile):  # Create a function that asks OSRM for route distance and time.
    start = f"{from_coordinates[1]},{from_coordinates[0]}"  # OSRM requires start coordinates as longitude,latitude.
    end = f"{to_coordinates[1]},{to_coordinates[0]}"  # OSRM requires end coordinates as longitude,latitude.
    url = f"{OSRM_ROUTE_BASE_URL}/{profile}/{start};{end}"  # Build the OSRM URL with the selected profile, such as driving or walking.
    params = {"overview": "false", "steps": "false"}  # Ask OSRM for summary distance/time only, not full geometry or turn steps.
    try:  # Try the API request because public route services can be unavailable.
        response = requests.get(url, params=params, timeout=5)  # Send a GET request to OSRM with the route parameters.
        response.raise_for_status()  # Raise an error if OSRM returns a bad HTTP status.
        data = response.json()  # Convert the JSON response into Python data.
        meters = data["routes"][0]["distance"]  # Read real route distance in meters from OSRM.
        seconds = data["routes"][0]["duration"]  # Read estimated travel time in seconds from OSRM.
        distance_km = round(meters / 1000, 2)  # Convert meters into kilometers.
        minutes = max(1, round(seconds / 60))  # Convert seconds into minutes.
        return distance_km, minutes, "Real"  # Return real OSRM distance, time, and source type.
    except (requests.RequestException, KeyError, IndexError, ValueError):  # Handle network, JSON, and missing-route errors.
        return estimate_fallback_route(from_coordinates, to_coordinates, profile)  # Fall back to estimated distance and time.


def get_osrm_route_distance_from_coordinates(from_coordinates, to_coordinates):  # Create a compatibility function for code that only needs driving distance.
    distance_km, _minutes, source_type = get_osrm_route_from_coordinates(from_coordinates, to_coordinates, "driving")  # Get driving route data from OSRM.
    return distance_km, source_type  # Return only distance and source type.


def get_osrm_route_distance_km(from_location, to_location):  # Create a function that asks OSRM for real road distance.
    from_coordinates = get_stop_coordinates(from_location)  # Get coordinates for the starting location.
    to_coordinates = get_stop_coordinates(to_location)  # Get coordinates for the destination.
    if not from_coordinates or not to_coordinates:  # Check whether either location is missing coordinates.
        return None, "Estimated"  # Return no OSRM result when coordinates are missing.
    return get_osrm_route_distance_from_coordinates(from_coordinates, to_coordinates)  # Use the coordinate-based OSRM helper.


def read_metro_fare_slabs():  # Create a function that reads real Hyderabad Metro fare slabs from CSV.
    slabs = []  # Create an empty list for fare slabs.
    with METRO_FARE_CSV_PATH.open(newline="", encoding="utf-8") as fare_file:  # Open the CSV file safely.
        reader = csv.DictReader(fare_file)  # Read each CSV row as a dictionary.
        for row in reader:  # Loop through each fare slab row.
            max_km = float(row["max_km"]) if row["max_km"] else None  # Convert max distance to a number, or None for the final open-ended slab.
            slabs.append(  # Add one fare slab dictionary.
                {  # Start the slab dictionary.
                    "min_km": float(row["min_km"]),  # Store the minimum distance for this slab.
                    "max_km": max_km,  # Store the maximum distance for this slab.
                    "fare": int(row["fare_rupees"]),  # Store the official fare for this slab.
                }  # End the slab dictionary.
            )  # Finish adding the slab.
    return slabs  # Return all fare slabs.


def get_real_metro_fare(distance_km):  # Create a function that finds a metro fare from the real fare CSV.
    for slab in read_metro_fare_slabs():  # Loop through each fare slab from the CSV.
        if slab["max_km"] is None and distance_km > slab["min_km"]:  # Check the final open-ended fare slab.
            return slab["fare"]  # Return the final slab fare.
        if distance_km > slab["min_km"] and distance_km <= slab["max_km"]:  # Check whether distance falls inside this slab.
            return slab["fare"]  # Return the matching slab fare.
        if distance_km == 0 and slab["min_km"] == 0:  # Handle zero distance as the first slab.
            return slab["fare"]  # Return the first slab fare.
    return read_metro_fare_slabs()[-1]["fare"]  # Return the highest fare if nothing matched.


def estimate_bus_fare(distance_km):  # Create a function that estimates bus fare because no public TGSRTC city bus fare API is available.
    stages = max(1, round(distance_km / 2))  # Treat each stage as about 2 km for a simple city-bus estimate.
    fare = 10 + (stages * 5)  # Use a simple base fare plus stage-based fare.
    return min(max(fare, 15), 60)  # Keep the estimated city bus fare in a realistic sample range.


def build_hybrid_option(name, fare, time_minutes, distance_km, source_type, walking_distance_km=0, transport_changes=0):  # Create a function that builds one hybrid comparison option.
    return {  # Return one option dictionary.
        "option": name,  # Store the transport option name.
        "fare": round(fare),  # Store fare as a rounded rupee amount.
        "estimated_time": round(time_minutes),  # Store time as rounded minutes.
        "distance": round(distance_km, 2),  # Store distance in kilometers.
        "source_type": source_type,  # Store whether the data is Real or Estimated.
        "walking_distance": round(walking_distance_km, 2),  # Store walking distance so recommendations can avoid too much walking.
        "transport_changes": transport_changes,  # Store how many times the user may need to change transport.
    }  # End the option dictionary.


def count_transport_changes_for_route(route):  # Create a function that counts transport changes in a route plan.
    main_modes = []  # Create an empty list for non-walking transport modes.
    for step in route["steps"]:  # Loop through each travel instruction in the route.
        if step["mode"] != "Walk":  # Ignore walking because it is first-mile or last-mile movement.
            main_modes.append(step["mode"])  # Add the real transport mode, such as Metro or Bus.
    if len(main_modes) <= 1:  # Check whether there is only one ride mode.
        return 0  # Return zero changes because the user does not switch rides.
    return len(main_modes) - 1  # Return one less than the number of ride segments as the change count.


def normalize_score(value, lowest_value, highest_value):  # Create a function that turns any number into a 0 to 1 score.
    if highest_value == lowest_value:  # Check whether all options have the same value.
        return 0  # Return zero because no option is worse than another for this value.
    return (value - lowest_value) / (highest_value - lowest_value)  # Return a smaller score for better values and a bigger score for worse values.


def get_current_user_preferences():  # Create a function that reads the user's travel preferences from Streamlit.
    return {  # Return the preferences in one small dictionary.
        "travel_preference": st.session_state.get("travel_preference", "Balanced"),  # Read the selected recommendation style.
        "budget_limit": st.session_state.get("budget_limit", 0),  # Read the budget limit, or zero if there is no limit.
    }  # End the preferences dictionary.


def get_preference_weights(travel_preference):  # Create a function that chooses scoring weights from the user's preference.
    weights = {  # Start with balanced weights.
        "cost": 0.30,  # Give cost a normal balanced importance.
        "time": 0.30,  # Give travel time a normal balanced importance.
        "walking": 0.15,  # Give walking distance a smaller but useful importance.
        "changes": 0.10,  # Give transport changes a smaller but useful importance.
        "traffic": 0.10,  # Give traffic risk a small balanced importance.
        "metro": 0.05,  # Give metro preference a small balanced importance.
    }  # End the balanced weights.
    if travel_preference == "Cheapest":  # Check whether the user mainly wants to save money.
        weights.update({"cost": 0.55, "time": 0.20, "walking": 0.10, "changes": 0.05, "traffic": 0.05, "metro": 0.05})  # Make fare the most important factor.
    elif travel_preference == "Fastest":  # Check whether the user mainly wants the quickest route.
        weights.update({"cost": 0.15, "time": 0.55, "walking": 0.10, "changes": 0.05, "traffic": 0.10, "metro": 0.05})  # Make travel time the most important factor.
    elif travel_preference == "Less walking":  # Check whether the user wants to reduce walking.
        weights.update({"cost": 0.15, "time": 0.20, "walking": 0.45, "changes": 0.10, "traffic": 0.05, "metro": 0.05})  # Make walking distance the most important factor.
    elif travel_preference == "Metro preferred":  # Check whether the user wants metro when possible.
        weights.update({"cost": 0.20, "time": 0.20, "walking": 0.10, "changes": 0.10, "traffic": 0.10, "metro": 0.30})  # Reward metro options more strongly.
    elif travel_preference == "Avoid traffic":  # Check whether the user wants to avoid road traffic.
        weights.update({"cost": 0.15, "time": 0.20, "walking": 0.10, "changes": 0.10, "traffic": 0.35, "metro": 0.10})  # Make traffic risk the most important factor.
    return weights  # Return the final scoring weights.


def get_option_traffic_risk(option):  # Create a function that estimates how much traffic can affect one option.
    option_name = option["option"]  # Read the transport option name.
    if option_name in ["Metro", "Walk Only"]:  # Metro and walking do not depend much on road traffic.
        return 0  # Return no traffic risk.
    if option_name == "Rapido Bike":  # Bikes can move through traffic better than cars.
        return 0.45  # Return medium-low traffic risk.
    if option_name == "Bus":  # Buses can be delayed by stops and road traffic.
        return 0.85  # Return high traffic risk.
    return 0.75  # Autos and cabs are road-based, so they have traffic risk.


def get_option_metro_penalty(option):  # Create a function that helps the score prefer Metro when the user asks for it.
    if option["option"] == "Metro":  # Check whether this option is Metro.
        return 0  # Return no penalty because this matches the preference.
    return 1  # Return a penalty for non-metro options.


def get_budget_penalty(option, budget_limit):  # Create a function that penalizes options above the user's budget.
    if budget_limit <= 0:  # Check whether the user did not enter a budget.
        return 0  # Return no penalty when there is no budget limit.
    if option["fare"] <= budget_limit:  # Check whether the fare fits inside the budget.
        return 0  # Return no penalty for affordable options.
    extra_cost = option["fare"] - budget_limit  # Calculate how many rupees the option is over budget.
    return min(0.35, extra_cost / max(budget_limit, 1))  # Return a strong but capped penalty for going over budget.


def add_recommendation_scores(options, user_preferences):  # Create a function that scores every transport option using user preferences.
    travel_preference = user_preferences["travel_preference"]  # Read the user's main preference.
    budget_limit = user_preferences["budget_limit"]  # Read the user's budget limit.
    weights = get_preference_weights(travel_preference)  # Get scoring weights for this preference.
    fares = [option["fare"] for option in options]  # Collect all fares so the app can compare low and high cost.
    times = [option["estimated_time"] for option in options]  # Collect all travel times so the app can compare slow and fast options.
    walks = [option["walking_distance"] for option in options]  # Collect all walking distances so the app can prefer easier routes.
    changes = [option["transport_changes"] for option in options]  # Collect all transport changes so the app can prefer simpler trips.
    for option in options:  # Loop through each option and calculate one final score.
        cost_score = normalize_score(option["fare"], min(fares), max(fares))  # Score cost, where cheaper is better.
        time_score = normalize_score(option["estimated_time"], min(times), max(times))  # Score time, where faster is better.
        walking_score = normalize_score(option["walking_distance"], min(walks), max(walks))  # Score walking, where less walking is better.
        change_score = normalize_score(option["transport_changes"], min(changes), max(changes))  # Score changes, where fewer changes are better.
        traffic_score = get_option_traffic_risk(option)  # Score traffic risk, where lower risk is better.
        metro_score = get_option_metro_penalty(option)  # Score metro preference, where Metro is better.
        budget_score = get_budget_penalty(option, budget_limit)  # Add an extra penalty when an option is over budget.
        final_score = (cost_score * weights["cost"]) + (time_score * weights["time"]) + (walking_score * weights["walking"]) + (change_score * weights["changes"]) + (traffic_score * weights["traffic"]) + (metro_score * weights["metro"]) + budget_score  # Mix all factors into one score.
        option["recommendation_score"] = round(final_score * 100, 1)  # Store the balanced score as a 0 to 100 number.
        option["traffic_risk"] = round(traffic_score, 2)  # Store traffic risk so users can understand the recommendation.
        option["within_budget"] = budget_limit <= 0 or option["fare"] <= budget_limit  # Store whether the option fits the user's budget.
    return options  # Return the updated options list.


def find_recommended_options(options):  # Create a function that finds the three intelligent recommendations.
    cheapest_option = min(options, key=lambda option: option["fare"])  # Recommend the lowest fare as the cheapest route.
    fastest_option = min(options, key=lambda option: option["estimated_time"])  # Recommend the lowest time as the fastest route.
    balanced_option = min(options, key=lambda option: option["recommendation_score"])  # Recommend the lowest score as the balanced route.
    return cheapest_option, fastest_option, balanced_option  # Return all three recommendation winners.


def build_app_based_options(distance_km, driving_minutes, source_type):  # Create a function that builds estimated app-based and auto options using OSRM driving time.
    return [  # Return all estimated private ride options.
        build_hybrid_option("Rapido Bike", calculate_ride_cost(20, 8, distance_km), max(5, round(driving_minutes * 0.9)), distance_km, source_type),  # Rapido Bike uses OSRM driving time with a small bike-speed adjustment.
        build_hybrid_option("Ola Auto", calculate_ride_cost(35, 17, distance_km), driving_minutes, distance_km, source_type),  # Ola Auto uses OSRM driving time.
        build_hybrid_option("Uber Auto", calculate_ride_cost(35, 17, distance_km), driving_minutes, distance_km, source_type),  # Uber Auto uses OSRM driving time.
        build_hybrid_option("Local Auto", calculate_ride_cost(30, 15, distance_km), max(5, round(driving_minutes * 1.05)), distance_km, source_type),  # Local Auto uses OSRM driving time with a small local-stop adjustment.
        build_hybrid_option("Cab Mini", calculate_ride_cost(60, 22, distance_km), max(5, round(driving_minutes * 0.95)), distance_km, source_type),  # Cab Mini uses OSRM driving time with a small car-speed adjustment.
    ]  # End the estimated ride options list.


def build_bus_option(distance_km, driving_minutes, source_type):  # Create a function that builds the estimated bus option.
    fare = estimate_bus_fare(distance_km)  # Estimate bus fare using distance stages.
    time_minutes = max(8, round(driving_minutes * 1.35))  # Estimate bus time as slower than OSRM driving due to stops.
    return build_hybrid_option("Bus", fare, time_minutes, distance_km, source_type)  # Return the bus option.


def build_metro_option(route):  # Create a function that builds the real metro fare option when metro is available.
    metro_distance = get_main_route_distance(route)  # Use the route's main metro distance from the database.
    metro_fare = get_real_metro_fare(metro_distance)  # Look up fare from the official-fare CSV slabs.
    walking_distance = get_walking_distance_from_route(route)  # Calculate walking distance around the metro trip.
    transport_changes = count_transport_changes_for_route(route)  # Count transfers or mode changes in the route.
    total_distance = metro_distance + walking_distance  # Add metro and walking distance.
    total_time = route["total_minutes"]  # Use the app's route time because it already includes walk and metro steps.
    return build_hybrid_option("Metro", metro_fare, total_time, total_distance, "Real", walking_distance, transport_changes)  # Return the real metro fare option.


def compare_ride_options(route, user_preferences):  # Create a function that compares hybrid real-data and estimated-fare options.
    from_location, to_location = get_location_pair_from_route(route)  # Get the selected route start and destination.
    real_from_coordinates = route.get("real_from_coordinates")  # Read real searched From coordinates when available.
    real_to_coordinates = route.get("real_to_coordinates")  # Read real searched To coordinates when available.
    if real_from_coordinates and real_to_coordinates:  # Check whether both real searched places have coordinates.
        osrm_distance, driving_minutes, distance_source = get_osrm_route_from_coordinates(real_from_coordinates, real_to_coordinates, "driving")  # Use real typed-place coordinates for OSRM driving distance and time.
        walking_distance, walking_minutes, walking_source = get_osrm_route_from_coordinates(real_from_coordinates, real_to_coordinates, "walking")  # Use real typed-place coordinates for OSRM walking distance and time.
    else:  # Use known sample stop coordinates when real typed places are not available.
        from_coordinates = get_stop_coordinates(from_location)  # Get coordinates for the known From stop.
        to_coordinates = get_stop_coordinates(to_location)  # Get coordinates for the known To stop.
        osrm_distance, driving_minutes, distance_source = get_osrm_route_from_coordinates(from_coordinates, to_coordinates, "driving")  # Get OSRM driving distance and time for known stops.
        walking_distance, walking_minutes, walking_source = get_osrm_route_from_coordinates(from_coordinates, to_coordinates, "walking")  # Get OSRM walking distance and time for known stops.
    options = build_app_based_options(osrm_distance, driving_minutes, distance_source)  # Build app-based ride options using OSRM driving data.
    options.append(build_bus_option(osrm_distance, driving_minutes, distance_source))  # Add estimated bus fare using OSRM distance and adjusted OSRM time.
    options.append(build_hybrid_option("Walk Only", 0, walking_minutes, walking_distance, walking_source, walking_distance, 0))  # Add a walking option using OSRM walking data.
    if has_metro_step(route):  # Check whether metro is available in the route plan.
        options.append(build_metro_option(route))  # Add Metro using real fare CSV data.
    options = add_recommendation_scores(options, user_preferences)  # Add a preference-based recommendation score to every option.
    cheapest_option, fastest_option, best_overall_option = find_recommended_options(options)  # Find cheapest, fastest, and balanced routes.
    return options, cheapest_option, fastest_option, best_overall_option, distance_source  # Return options, winners, and road-distance source.


def get_transport_icon_details(option_name):  # Create a function that chooses a simple icon label for each transport type.
    if "Metro" in option_name:  # Check whether this option is metro.
        return "M", "transport-icon-metro"  # Return a metro icon letter and color class.
    if "Bike" in option_name:  # Check whether this option is a bike ride.
        return "B", "transport-icon-bike"  # Return a bike icon letter and color class.
    if "Auto" in option_name:  # Check whether this option is any auto type.
        return "A", "transport-icon-auto"  # Return an auto icon letter and color class.
    if "Cab" in option_name or "Car" in option_name:  # Check whether this option is a car or cab.
        return "C", "transport-icon-car"  # Return a car icon letter and color class.
    if "Bus" in option_name:  # Check whether this option is bus.
        return "S", "transport-icon-bus"  # Return a bus icon letter and color class.
    if "Walk" in option_name:  # Check whether this option is walking.
        return "W", "transport-icon-walk"  # Return a walking icon letter and color class.
    return "R", "transport-icon-car"  # Return a default route icon letter and color class.


def build_recommendation_badge(label):  # Create a function that builds one colored recommendation badge.
    badge_class = "winner-label"  # Start with the base badge class.
    if label == "Cheapest Route":  # Check whether this is the cheapest badge.
        badge_class += " winner-label-cheapest"  # Add the green badge style.
    elif label == "Fastest Route":  # Check whether this is the fastest badge.
        badge_class += " winner-label-fastest"  # Add the red badge style.
    elif label == "Preference Match":  # Check whether this is the smart recommendation badge.
        badge_class += " winner-label-preference"  # Add the purple badge style.
    elif label == "Over Budget":  # Check whether this is the budget warning badge.
        badge_class += " winner-label-budget"  # Add the amber badge style.
    return f"<span class='{badge_class}'>{label}</span>"  # Return the badge HTML.


def show_comparison_card(option, cheapest_option, fastest_option, best_overall_option):  # Create a function that displays one ride comparison card.
    labels = []  # Create an empty list for winner labels.
    if option["option"] == cheapest_option["option"]:  # Check whether this option is the cheapest.
        labels.append("Cheapest Route")  # Add the cheapest recommendation label.
    if option["option"] == fastest_option["option"]:  # Check whether this option is the fastest.
        labels.append("Fastest Route")  # Add the fastest recommendation label.
    if option["option"] == best_overall_option["option"]:  # Check whether this option is best overall.
        labels.append("Preference Match")  # Add the preference-based recommendation label.
    if not option["within_budget"]:  # Check whether this option is above the user's budget.
        labels.append("Over Budget")  # Add an over-budget label.
    icon_label, icon_class = get_transport_icon_details(option["option"])  # Get the transport icon label and style.
    label_html = "".join(build_recommendation_badge(label) for label in labels)  # Convert labels into colored HTML badges.
    highlight_class = " compare-card-highlight" if labels else ""  # Highlight cards that win at least one category.
    st.markdown(  # Display the ride comparison card.
        dedent(  # Remove Python indentation from the HTML before rendering.
            f"""
            <div class="compare-card{highlight_class}">
                <div class="compare-header">
                    <div class="transport-icon {icon_class}">{icon_label}</div>
                    <div>
                        <div class="compare-title">{option['option']}</div>
                        <div class="compare-meta">Data Source: {option['source_type']}</div>
                    </div>
                </div>
                <div class="compare-grid">
                    <div class="compare-stat"><div class="compare-stat-label">Fare</div><div class="compare-stat-value">Rs. {option['fare']}</div></div>
                    <div class="compare-stat"><div class="compare-stat-label">Time</div><div class="compare-stat-value">{option['estimated_time']} mins</div></div>
                    <div class="compare-stat"><div class="compare-stat-label">Distance</div><div class="compare-stat-value">{option['distance']} km</div></div>
                    <div class="compare-stat"><div class="compare-stat-label">Walking</div><div class="compare-stat-value">{option['walking_distance']} km</div></div>
                    <div class="compare-stat"><div class="compare-stat-label">Changes</div><div class="compare-stat-value">{option['transport_changes']}</div></div>
                    <div class="compare-stat"><div class="compare-stat-label">Score</div><div class="compare-stat-value">{option['recommendation_score']}/100</div></div>
                </div>
                <div class="compare-meta">Traffic Risk: {option['traffic_risk']} | Budget: {"OK" if option['within_budget'] else "Over limit"}</div>
                <div class="badge-stack">{label_html}</div>
            </div>
            """,  # End the comparison card HTML.
        ),  # Finish cleaning the HTML indentation.
        unsafe_allow_html=True,  # Allow Streamlit to render the custom comparison card.
    )  # Finish displaying the comparison card.


def show_ride_compare(route):  # Create a function that displays the full Ride Compare feature.
    user_preferences = get_current_user_preferences()  # Read the user's travel preferences.
    options, cheapest_option, fastest_option, best_overall_option, distance_source = compare_ride_options(route, user_preferences)  # Calculate all ride options and winners.
    st.subheader("Fare Comparison")  # Show the fare comparison section heading.
    st.caption(f"Route calculation source: {distance_source} OSRM/OpenStreetMap distance and time when available; fallback is estimated from coordinates.")  # Explain the route source.
    summary_columns = st.columns(3)  # Create three summary columns for winner cards.
    with summary_columns[0]:  # Use the first column for cheapest option.
        show_metric_card("Cheapest", f"{cheapest_option['option']} - Rs. {cheapest_option['fare']}")  # Show cheapest option.
    with summary_columns[1]:  # Use the second column for fastest option.
        show_metric_card("Fastest", f"{fastest_option['option']} - {fastest_option['estimated_time']} mins")  # Show fastest option.
    with summary_columns[2]:  # Use the third column for best overall option.
        show_metric_card("Preference Match", f"{best_overall_option['option']} - Score {best_overall_option['recommendation_score']}")  # Show preference-based recommendation.
    budget_text = "No budget limit" if user_preferences["budget_limit"] <= 0 else f"Budget limit: Rs. {user_preferences['budget_limit']}"  # Build a simple budget label.
    st.info(f"Recommendation preference: {user_preferences['travel_preference']} | {budget_text}. The score changes based on your preference and still considers cost, travel time, walking distance, transport changes, traffic risk, and metro preference.")  # Explain the recommendation engine in simple words.
    comparison_rows = []  # Create an empty list for table rows.
    for option in options:  # Loop through every ride option.
        recommendation_badges = []  # Create an empty list for recommendation labels in the table.
        if option["option"] == cheapest_option["option"]:  # Check whether this row is the cheapest recommendation.
            recommendation_badges.append("Cheapest")  # Add a cheapest badge.
        if option["option"] == fastest_option["option"]:  # Check whether this row is the fastest recommendation.
            recommendation_badges.append("Fastest")  # Add a fastest badge.
        if option["option"] == best_overall_option["option"]:  # Check whether this row is the balanced recommendation.
            recommendation_badges.append("Preference Match")  # Add a preference-based badge.
        if not option["within_budget"]:  # Check whether this row is above the user's budget.
            recommendation_badges.append("Over Budget")  # Add an over-budget badge.
        comparison_rows.append(  # Add one table row dictionary.
            {  # Start one table row.
                "Transport Option": option["option"],  # Store the option name.
                "Recommendation Badges": ", ".join(recommendation_badges) if recommendation_badges else "-",  # Store recommendation badges.
                "Estimated/Real Fare": f"Rs. {option['fare']}",  # Store the fare.
                "Estimated Time": f"{option['estimated_time']} mins",  # Store the estimated time.
                "Distance": f"{option['distance']} km",  # Store distance.
                "Walking Distance": f"{option['walking_distance']} km",  # Store walking distance.
                "Transport Changes": option["transport_changes"],  # Store how many times the user changes transport.
                "Traffic Risk": option["traffic_risk"],  # Store traffic risk for avoid-traffic preference.
                "Preference Score": option["recommendation_score"],  # Store the score used for preference recommendation.
                "Within Budget": "Yes" if option["within_budget"] else "No",  # Show whether the option fits the user's budget.
                "Data Source Type": option["source_type"],  # Store whether the data is Real or Estimated.
            }  # End one table row.
        )  # Finish adding the row.
    st.dataframe(comparison_rows, use_container_width=True, hide_index=True)  # Display a clean fare comparison table.
    with st.expander("How the preference score works"):  # Add an expandable beginner explanation.
        st.write("The app compares each option against the others for cost, travel time, walking distance, transport changes, traffic risk, and metro preference.")  # Explain the first scoring step.
        st.write("When you choose Cheapest, Fastest, Less walking, Metro preferred, or Avoid traffic, the app gives that factor more weight in the score.")  # Explain how preferences change weights.
        st.write("If you enter a budget limit, options above that amount get an extra penalty. Lower score is better.")  # Explain budget and score direction.
    st.warning("App-based fares are estimated and may vary due to surge pricing, demand, waiting charges, and availability.")  # Show the required fare disclaimer.
    card_columns = st.columns(2)  # Create two columns for comparison cards.
    for index, option in enumerate(options):  # Loop through each ride option with its index.
        with card_columns[index % 2]:  # Alternate cards between the two columns.
            show_comparison_card(option, cheapest_option, fastest_option, best_overall_option)  # Show one comparison card.


def get_route_map_points(route):  # Create a function that turns route steps into map points.
    route_points = []  # Create an empty list for the route line coordinates.
    for step in route["steps"]:  # Loop through every route step.
        if "from" in step:  # Check whether this step has a named starting stop.
            from_coordinates = get_stop_coordinates(step["from"])  # Get coordinates for the starting stop.
            if from_coordinates and from_coordinates not in route_points:  # Add the point only if it exists and is not already in the list.
                route_points.append(from_coordinates)  # Add the starting stop coordinates to the route line.
        if "to" in step:  # Check whether this step has a named ending stop.
            to_coordinates = get_stop_coordinates(step["to"])  # Get coordinates for the ending stop.
            if to_coordinates and to_coordinates not in route_points:  # Add the point only if it exists and is not already in the list.
                route_points.append(to_coordinates)  # Add the ending stop coordinates to the route line.
    return route_points  # Return the list of coordinates for drawing the map route.


def create_hyderabad_map(route, from_location, to_location):  # Create a function that builds the interactive Hyderabad route map.
    hyderabad_center = [17.3850, 78.4867]  # Store Hyderabad center coordinates so the map opens around the city.
    travel_map = folium.Map(location=hyderabad_center, zoom_start=11, tiles="OpenStreetMap")  # Create a Folium map using OpenStreetMap tiles.
    all_stops = get_all_stops_for_map()  # Read all stops from the database so we can show them as markers.

    for stop in all_stops:  # Loop through every stop that should appear on the map.
        marker_color = "blue"  # Use blue as the default marker color for ordinary stops.
        if "Metro" in stop["area_type"]:  # Check whether the stop category mentions Metro.
            marker_color = "purple"  # Use purple markers for metro stations and metro areas.
        folium.Marker(  # Create a marker for this stop.
            location=[stop["latitude"], stop["longitude"]],  # Place the marker at the stop coordinates.
            popup=f"{stop['name']} - {stop['area_type']}",  # Show the stop name and type when the marker is clicked.
            tooltip=stop["name"],  # Show the stop name when the user hovers over the marker.
            icon=folium.Icon(color=marker_color, icon="info-sign"),  # Use a simple colored icon for the marker.
        ).add_to(travel_map)  # Add this stop marker to the map.

    from_coordinates = get_stop_coordinates(from_location)  # Get coordinates for the selected From location.
    to_coordinates = get_stop_coordinates(to_location)  # Get coordinates for the selected To location.

    if from_coordinates:  # Check whether the From location has coordinates.
        folium.Marker(  # Create a special marker for the start location.
            location=from_coordinates,  # Place the marker at the From coordinates.
            popup=f"From: {from_location}",  # Show a From popup when clicked.
            tooltip=f"From: {from_location}",  # Show a From tooltip when hovered.
            icon=folium.Icon(color="green", icon="play"),  # Use a green icon for the start.
        ).add_to(travel_map)  # Add the From marker to the map.

    if to_coordinates:  # Check whether the To location has coordinates.
        folium.Marker(  # Create a special marker for the destination.
            location=to_coordinates,  # Place the marker at the To coordinates.
            popup=f"To: {to_location}",  # Show a To popup when clicked.
            tooltip=f"To: {to_location}",  # Show a To tooltip when hovered.
            icon=folium.Icon(color="red", icon="stop"),  # Use a red icon for the destination.
        ).add_to(travel_map)  # Add the To marker to the map.

    if route and route.get("transfer_stop"):  # Check whether the route has a transfer stop.
        transfer_coordinates = get_stop_coordinates(route["transfer_stop"])  # Get coordinates for the transfer stop.
        if transfer_coordinates:  # Check whether transfer coordinates exist.
            folium.Marker(  # Create a marker for the transfer stop.
                location=transfer_coordinates,  # Place the marker at the transfer coordinates.
                popup=f"Transfer: {route['transfer_stop']}",  # Show a transfer popup when clicked.
                tooltip=f"Transfer: {route['transfer_stop']}",  # Show a transfer tooltip when hovered.
                icon=folium.Icon(color="orange", icon="random"),  # Use orange to show a transfer point.
            ).add_to(travel_map)  # Add the transfer marker to the map.

    route_points = get_route_map_points(route)  # Convert route steps into map line coordinates.
    if len(route_points) >= 2:  # Draw a route line only when there are at least two points.
        folium.PolyLine(  # Create a line that shows the route path.
            locations=route_points,  # Use the route coordinates as the line path.
            color="#1b8a5a",  # Draw the route line in a clean Hyderabad-themed green.
            weight=5,  # Make the route line thick enough to see.
            opacity=0.85,  # Keep the route line mostly solid.
            tooltip="Suggested route",  # Show a label when hovering over the route line.
        ).add_to(travel_map)  # Add the route line to the map.
        travel_map.fit_bounds(route_points)  # Zoom the map so the full route is visible.

    return travel_map  # Return the finished Folium map to Streamlit.


def show_metric_card(label, value):  # Create a function that displays one route summary card.
    st.markdown(  # Render the metric card as small HTML.
        dedent(  # Remove Python indentation from the card HTML before displaying it.
            f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,  # End the metric card HTML.
        ),  # Finish removing extra indentation from the card HTML.
        unsafe_allow_html=True,  # Allow Streamlit to render the custom card HTML.
    )  # Finish displaying the card.


def show_step_card(number, step):  # Create a function that displays one route instruction card.
    st.markdown(  # Render one route step card as small HTML.
        dedent(  # Remove Python indentation from the step HTML before displaying it.
            f"""
        <div class="step-card">
            <div class="step-title">{number}. {step['instruction']}</div>
            <div class="step-meta">Mode: {step['mode']} | Time: {step['minutes']} mins | Cost: Rs. {step['fare']} | Distance: {step['distance_km']} km</div>
            <div class="step-note">{step['notes']}</div>
        </div>
        """,  # End the route step HTML.
        ),  # Finish removing extra indentation from the step HTML.
        unsafe_allow_html=True,  # Allow Streamlit to render the custom card HTML.
    )  # Finish displaying the route step card.


def show_route_results(route, from_location, to_location):  # Create a function that displays the full route result area.
    st.markdown('<div class="route-card">', unsafe_allow_html=True)  # Start a modern route result card.
    st.markdown(  # Show the route title inside a professional card header.
        f"<div class='route-title-row'><div class='route-title'>{from_location} to {to_location}</div><div class='route-pill'>{route['route_type']}</div></div>",  # Build the route card title row.
        unsafe_allow_html=True,  # Allow Streamlit to render the title row HTML.
    )  # Finish showing the route title.
    show_transport_badges(route)  # Show transport type badges for this route.
    if route["route_type"] == "1-transfer route":  # Check whether the route includes a transfer.
        st.caption(f"Transfer at {route['transfer_stop']}")  # Show the transfer stop as a small caption.
    show_save_favorite_button(from_location, to_location)  # Let logged-in users save this route as a favorite.

    traffic_delay = estimate_traffic_delay(route)  # Estimate extra road traffic delay for the selected route.
    traffic_adjusted_time = route["total_minutes"] + traffic_delay  # Add traffic delay to the base trip time.
    cost_column, time_column, delay_column, distance_column = st.columns(4)  # Create four responsive columns for summary cards.
    with cost_column:  # Use the first column for cost.
        show_metric_card("Total Cost", f"Rs. {route['total_fare']}")  # Show the total trip cost.
    with time_column:  # Use the second column for time.
        show_metric_card("Total Time", f"{route['total_minutes']} mins")  # Show the total trip time.
    with delay_column:  # Use the third column for traffic delay.
        show_metric_card("With Traffic", f"{traffic_adjusted_time} mins")  # Show the traffic-adjusted trip time.
    with distance_column:  # Use the fourth column for distance.
        show_metric_card("Distance", f"{route['total_distance_km']} km")  # Show the total trip distance.
    st.caption(f"Estimated traffic delay: {traffic_delay} mins based on road-based steps in this sample route.")  # Explain the delay estimate simply.
    st.markdown("</div>", unsafe_allow_html=True)  # End the white result section.

    with st.spinner("Comparing fares, time, and preferences..."):  # Show a loading message while OSRM and comparison logic run.
        show_ride_compare(route)  # Show ride-app, auto, car, and Metro + Walk comparison options.

    st.subheader("Step-by-Step Instructions")  # Add a heading for route steps.
    for number, step in enumerate(route["steps"], start=1):  # Loop through each route step.
        show_step_card(number, step)  # Display one route step card.

    st.subheader("Interactive Route Map")  # Add a heading above the map.
    route_map = create_hyderabad_map(route, from_location, to_location)  # Build a Folium map for the selected route.
    st_folium(route_map, width=None, height=460)  # Embed the Folium map inside Streamlit with responsive width.


st.set_page_config(page_title="LastMile Hyderabad Travel Planner", page_icon="L", layout="wide")  # Set the browser tab title, icon, and page width.

initialize_database()  # Create the SQLite tables and add sample Hyderabad data when the app starts.

setup_session_state()  # Prepare search history and default route choices.

theme_mode = st.sidebar.selectbox("Theme Mode", ["Light", "Dark"], index=["Light", "Dark"].index(st.session_state["theme_mode"]))  # Let the user choose light or dark mode.

st.session_state["theme_mode"] = theme_mode  # Save the selected theme so it stays after reruns.

add_custom_css(theme_mode)  # Apply the custom modern transport-app styling.

show_sidebar()  # Show project information in the sidebar.

st.markdown(  # Display a clean hero section at the top of the page.
    dedent(  # Remove Python indentation from the hero HTML before displaying it.
        """
    <div class="hero-box">
        <div class="hero-title">LastMile - Hyderabad Local Travel Planner</div>
        <p class="hero-subtitle">Plan metro, bus, walking, and share-auto connections across sample Hyderabad stops.</p>
    </div>
    """,  # End the hero section HTML.
    ),  # Finish removing extra indentation from the hero HTML.
    unsafe_allow_html=True,  # Allow Streamlit to render the custom hero HTML.
)  # Finish displaying the hero section.

locations = get_all_stop_names()  # Read all available Hyderabad locations from the SQLite database.

popular_routes = [  # Create a list of popular Hyderabad route shortcuts.
    ("Ameerpet", "Hitech City"),  # Add a popular metro route.
    ("Miyapur", "Ameerpet"),  # Add a route that can use one transfer.
    ("Secunderabad", "Uppal"),  # Add an east-side metro route.
    ("LB Nagar", "Dilsukhnagar"),  # Add a short red-line route.
]  # End the popular routes list.

st.subheader("Popular Hyderabad Routes")  # Show a heading for quick route shortcuts.
popular_columns = st.columns(len(popular_routes))  # Create one column per popular route.
for route_index, popular_route in enumerate(popular_routes):  # Loop through each popular route.
    with popular_columns[route_index]:  # Put each popular route button in its own column.
        route_label = f"{popular_route[0]} to {popular_route[1]}"  # Build the button label.
        if st.button(route_label, key=f"popular_{route_index}"):  # Create a clickable popular route button.
            set_popular_route(popular_route[0], popular_route[1])  # Save the selected popular route in session state.
            st.rerun()  # Rerun the app so the dropdowns update immediately.

show_favorite_routes_panel()  # Show saved favorite routes for logged-in users.

show_analytics_dashboard()  # Show charts and summary metrics for routes and searches.

st.markdown('<div class="section-card">', unsafe_allow_html=True)  # Start a clean search section.
st.subheader("Search Route")  # Show a compact heading for the search form.
from_column, to_column, preference_column, button_column = st.columns([1, 1, 1, 0.7])  # Create columns for a neat desktop layout.

from_index = locations.index(st.session_state["from_choice"]) if st.session_state["from_choice"] in locations else 0  # Find the saved From dropdown index.

with from_column:  # Place the From dropdown in the first column.
    from_location = st.selectbox("From Location", locations, index=from_index)  # Create a dropdown for the starting location.
    typed_from_location = st.text_input("Search any From Location", placeholder="Example: Charminar, Hyderabad")  # Let users type any Hyderabad location.
    from_place_suggestions = search_nominatim_locations(typed_from_location) if typed_from_location else []  # Get Nominatim autocomplete suggestions for From text.
    from_suggestion_label = None  # Start with no selected From suggestion.
    if from_place_suggestions:  # Check whether Nominatim returned From suggestions.
        from_suggestion_label = st.selectbox("From autocomplete suggestions", build_suggestion_labels(from_place_suggestions))  # Show From autocomplete options.

default_to_index = locations.index(st.session_state["to_choice"]) if st.session_state["to_choice"] in locations else 1  # Find the saved To dropdown index.

with to_column:  # Place the To dropdown in the second column.
    to_location = st.selectbox("To Location", locations, index=default_to_index)  # Create a dropdown for the destination location.
    typed_to_location = st.text_input("Search any To Location", placeholder="Example: Gachibowli, Hyderabad")  # Let users type any Hyderabad destination.
    to_place_suggestions = search_nominatim_locations(typed_to_location) if typed_to_location else []  # Get Nominatim autocomplete suggestions for To text.
    to_suggestion_label = None  # Start with no selected To suggestion.
    if to_place_suggestions:  # Check whether Nominatim returned To suggestions.
        to_suggestion_label = st.selectbox("To autocomplete suggestions", build_suggestion_labels(to_place_suggestions))  # Show To autocomplete options.

preference_options = ["Cheapest", "Fastest", "Less walking", "Metro preferred", "Avoid traffic"]  # Store the available user travel preferences.
saved_preference = st.session_state["travel_preference"] if st.session_state["travel_preference"] in preference_options else "Cheapest"  # Use a safe preference value.
preference_index = preference_options.index(saved_preference)  # Find the saved preference position for the dropdown.

with preference_column:  # Place user travel preferences in the third column.
    travel_preference = st.selectbox("Travel Preference", preference_options, index=preference_index)  # Let the user choose how recommendations should behave.
    budget_limit = st.number_input("Budget Limit Rs.", min_value=0, max_value=2000, value=st.session_state["budget_limit"], step=10)  # Let the user enter a maximum budget.
    st.caption("Use 0 for no budget limit.")  # Explain the budget field simply.

with button_column:  # Place the search button in the third column.
    st.write("")  # Add small vertical spacing so the button aligns with dropdowns.
    search_clicked = st.button("Search Route")  # Create a button and store whether the user clicked it.
st.markdown("</div>", unsafe_allow_html=True)  # End the clean search section.

if search_clicked:  # Check if the Search Route button was clicked.
    st.markdown("<div class='loading-strip'></div>", unsafe_allow_html=True)  # Show a small animated loading bar while the app searches.
    st.session_state["travel_preference"] = travel_preference  # Save the user's selected travel preference.
    st.session_state["budget_limit"] = budget_limit  # Save the user's budget limit.
    st.session_state["current_route"] = None  # Clear the previous route before starting a new search.
    st.session_state["current_from_location"] = None  # Clear the previous From result before searching.
    st.session_state["current_to_location"] = None  # Clear the previous To result before searching.
    selected_from_suggestion = get_selected_suggestion(from_suggestion_label, from_place_suggestions) if from_suggestion_label else None  # Read the selected From autocomplete result.
    selected_to_suggestion = get_selected_suggestion(to_suggestion_label, to_place_suggestions) if to_suggestion_label else None  # Read the selected To autocomplete result.
    resolved_from = resolve_location_for_route(from_location, typed_from_location, selected_from_suggestion, locations)  # Resolve From into a known route stop.
    resolved_to = resolve_location_for_route(to_location, typed_to_location, selected_to_suggestion, locations)  # Resolve To into a known route stop.
    matched_from_location = resolved_from["route_location"]  # Store the route-ready From stop.
    matched_to_location = resolved_to["route_location"]  # Store the route-ready To stop.
    from_suggestions = resolved_from.get("suggestions", [])  # Store local fuzzy From suggestions if the location is invalid.
    to_suggestions = resolved_to.get("suggestions", [])  # Store local fuzzy To suggestions if the location is invalid.
    if not matched_from_location or not matched_to_location:  # Check whether fuzzy matching failed for either field.
        st.error("I could not find one of those Hyderabad locations. Please choose an autocomplete suggestion or a sample stop from the dropdown.")  # Show a clear error message.
        if from_suggestions:  # Check whether From suggestions exist.
            st.write(f"From suggestions: {', '.join(from_suggestions)}")  # Show possible From matches.
        if to_suggestions:  # Check whether To suggestions exist.
            st.write(f"To suggestions: {', '.join(to_suggestions)}")  # Show possible To matches.
        show_nearby_locations("Nearby places around the selected From dropdown:", from_location, locations)  # Suggest nearby dropdown locations.
    elif matched_from_location == matched_to_location:  # Check whether the starting point and destination are the same.
        st.warning("Please choose different From and To locations.")  # Show a friendly warning if both locations match.
    else:  # Run this block when the user selected two different locations.
        if resolved_from["source"] == "Nominatim":  # Check whether From came from OpenStreetMap.
            st.info(f"Found From location at {resolved_from['latitude']:.5f}, {resolved_from['longitude']:.5f}. Routing through nearest sample stop: {matched_from_location} ({resolved_from['nearest_distance']} km away).")  # Explain the real geocoded From location.
        elif typed_from_location and matched_from_location != typed_from_location:  # Check whether fuzzy matching corrected the From text.
            st.info(f"Using '{matched_from_location}' for From Location.")  # Tell the user which From location will be used.
        if resolved_to["source"] == "Nominatim":  # Check whether To came from OpenStreetMap.
            st.info(f"Found To location at {resolved_to['latitude']:.5f}, {resolved_to['longitude']:.5f}. Routing through nearest sample stop: {matched_to_location} ({resolved_to['nearest_distance']} km away).")  # Explain the real geocoded To location.
        elif typed_to_location and matched_to_location != typed_to_location:  # Check whether fuzzy matching corrected the To text.
            st.info(f"Using '{matched_to_location}' for To Location.")  # Tell the user which To location will be used.
        with st.spinner("Finding the best local route..."):  # Show a loading message while the route search runs.
            route = find_route(matched_from_location, matched_to_location)  # Search the SQLite database for a route between the resolved locations.
        if route:  # Check whether the database returned a matching route.
            if resolved_from["latitude"] and resolved_to["latitude"]:  # Check whether both route ends have coordinates.
                route["real_from_coordinates"] = (resolved_from["latitude"], resolved_from["longitude"])  # Store real From coordinates for OSRM distance.
                route["real_to_coordinates"] = (resolved_to["latitude"], resolved_to["longitude"])  # Store real To coordinates for OSRM distance.
            add_search_history(matched_from_location, matched_to_location)  # Save the successful route search in history.
            st.session_state["current_route"] = route  # Save the route so it stays visible after Streamlit reruns.
            st.session_state["current_from_location"] = matched_from_location  # Save the matched From location for display.
            st.session_state["current_to_location"] = matched_to_location  # Save the matched To location for display.
        else:  # Run this block when there is no direct or transfer route in the database.
            st.error("No direct or 1-transfer sample route found for this pair yet.")  # Show a stronger error when no route exists.
            st.write("Try a nearby major stop or one of the popular Hyderabad routes above.")  # Suggest a practical next action.
            show_nearby_locations("Nearby places around your From location:", matched_from_location, locations)  # Suggest nearby From locations.
            show_nearby_locations("Nearby places around your To location:", matched_to_location, locations)  # Suggest nearby To locations.

if st.session_state["current_route"]:  # Check whether there is a saved route result to display.
    saved_route = st.session_state["current_route"]  # Read the saved route from session state.
    saved_from_location = st.session_state["current_from_location"]  # Read the saved From location from session state.
    saved_to_location = st.session_state["current_to_location"]  # Read the saved To location from session state.
    show_nearby_locations("Suggested nearby starts:", saved_from_location, locations)  # Show nearby places around the start.
    show_nearby_locations("Suggested nearby destinations:", saved_to_location, locations)  # Show nearby places around the destination.
    show_route_results(saved_route, saved_from_location, saved_to_location)  # Display summary cards, step cards, and the map.
