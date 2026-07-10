# Create a new file: frontend/route_component.py

import streamlit as st

def render_route_selector(routes_df, airports_dictionary, airports_df):
    """Renders the airport selectors and returns a dictionary of route details."""
    valid_origins = routes_df['ORIGIN_AIRPORT_ID'].unique()
    origin_airport_id = st.selectbox(
        "Select Origin Airport", 
        options=valid_origins, 
        format_func=lambda x: airports_dictionary[x]
    )
    
    valid_destinations = routes_df[routes_df['ORIGIN_AIRPORT_ID'] == origin_airport_id]
    dest_airport_id = st.selectbox(
        "Select Destination Airport", 
        options=valid_destinations['ARRIVAL_AIRPORT_ID'].tolist(), 
        format_func=lambda x: airports_dictionary[x]
    )

    selected_route = valid_destinations[valid_destinations['ARRIVAL_AIRPORT_ID'] == dest_airport_id].iloc[0]
    distance = selected_route['AVERAGE_DISTANCE']
    average_time_minutes = selected_route['AVERAGE_TIME']
    
    st.info(f"📏 Distance: {distance} miles")
    st.info(f"⏱️ Average Flight Time: {average_time_minutes} minutes")
    
    # Extract coordinates here so app.py doesn't have to
    origin_coords = airports_df[airports_df['ID'] == origin_airport_id].iloc[0]
    dest_coords = airports_df[airports_df['ID'] == dest_airport_id].iloc[0]
    
    return {
        "ORIGIN_AIRPORT_ID": origin_airport_id,
        "DESTINATION_AIRPORT_ID": dest_airport_id,
        "DISTANCE": distance,
        "AVERAGE_TIME_MINUTES": average_time_minutes,
        "ORIGIN_COORDS": origin_coords,
        "DEST_COORDS": dest_coords
    }