import streamlit as st
from database import fetch_airlines, fetch_airports, fetch_routes
from map_component import render_flight_map
from sidebar_component import render_sidebar
from route_component import render_route_selector 
from api_component import execute_and_display_results # <-- Import the new component

# --- DATA INITIALIZATION ---
airlines_dictionary = fetch_airlines()
airports_df = fetch_airports()
routes_df = fetch_routes()
airports_dictionary = dict(zip(airports_df['ID'], airports_df['AIRPORT']))

# --- CONFIGURATION ---
st.set_page_config(page_title="Aero-Optimize AI", page_icon="✈️", layout="wide")
API_URL = "http://127.0.0.1:8000/api/check_flight"

st.title("✈️ Aero-Optimize: Smart Dispatch System")
st.markdown("Predict flight delays and mathematically optimize standby crew assignments in real-time.")
st.divider()

# --- MAP & ROUTE SELECTION ---
st.subheader("🗺️ Route Selection")
col_map1, col_map2 = st.columns([1, 2])

with col_map1:
    route_data = render_route_selector(routes_df, airports_dictionary, airports_df)

with col_map2:
    st.pydeck_chart(render_flight_map(route_data["ORIGIN_COORDS"], route_data["DEST_COORDS"]))

st.divider()

# --- SIDEBAR: FLIGHT INPUTS ---
sidebar_data = render_sidebar(airlines_dictionary, route_data["AVERAGE_TIME_MINUTES"])

# --- API EXECUTION ---
if st.button("Run AI Analysis", type="primary", use_container_width=True):
    payload = {
        "ORIGIN_AIRPORT_ID": route_data["ORIGIN_AIRPORT_ID"],
        "DESTINATION_AIRPORT_ID": route_data["DESTINATION_AIRPORT_ID"],
        "DISTANCE": route_data["DISTANCE"],
        **sidebar_data 
    }
    
    # Pass the URL and payload to your new component
    execute_and_display_results(API_URL, payload)