import streamlit as st
import requests
import pandas as pd
import datetime
import os
import pydeck as pdk
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

@st.cache_resource 
def init_connection():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(db_url)

@st.cache_data 
def fetch_airlines():
    engine = init_connection()
    query = 'SELECT "ID", "AIRLINE" FROM public.airlines;' 
    df = pd.read_sql(query, engine)
    return dict(zip(df['ID'], df['AIRLINE']))

@st.cache_data
def fetch_airports():
    engine = init_connection()
    # Ensure you pull coordinates for the map
    query = 'SELECT "ID", "AIRPORT", "LATITUDE", "LONGITUDE" FROM public.airports;' 
    df = pd.read_sql(query, engine)
    return df

@st.cache_data
def fetch_routes():
    engine = init_connection()
    query = 'SELECT "ORIGIN_AIRPORT_ID", "ARRIVAL_AIRPORT_ID", "AVERAGE_DISTANCE", "AVERAGE_TIME" FROM public.route_averages;'
    df = pd.read_sql(query, engine)
    return df

# --- DATA INITIALIZATION ---
airlines_dictionary = fetch_airlines()
airports_df = fetch_airports()
routes_df = fetch_routes()

# Create a lookup dictionary for UI display
airports_dictionary = dict(zip(airports_df['ID'], airports_df['AIRPORT']))

# --- CONFIGURATION ---
st.set_page_config(page_title="Aero-Optimize AI", page_icon="✈️", layout="wide")
API_URL = "http://127.0.0.1:8000/api/check_flight"

# --- UI HEADER ---
st.title("✈️ Aero-Optimize: Smart Dispatch System")
st.markdown("Predict flight delays and mathematically optimize standby crew assignments in real-time.")
st.divider()

# --- MAP & ROUTE SELECTION (MAIN AREA) ---
st.subheader("🗺️ Route Selection")
col_map1, col_map2 = st.columns([1, 2])

with col_map1:
    # 1. Select Origin
    # Filter airports that actually exist as origins in the routes table
    valid_origins = routes_df['ORIGIN_AIRPORT_ID'].unique()
    origin_airport_id = st.selectbox(
        "Select Origin Airport", 
        options=valid_origins, 
        format_func=lambda x: airports_dictionary[x]
    )
    
    # 2. Filter valid destinations based on selected origin
    valid_destinations = routes_df[routes_df['ORIGIN_AIRPORT_ID'] == origin_airport_id]
    
    # 3. Select Destination
    dest_airport_id = st.selectbox(
        "Select Destination Airport", 
        options=valid_destinations['ARRIVAL_AIRPORT_ID'].tolist(), 
        format_func=lambda x: airports_dictionary[x]
    )

    # Extract the pre-calculated distance and time from your new table
    selected_route = valid_destinations[valid_destinations['ARRIVAL_AIRPORT_ID'] == dest_airport_id].iloc[0]
    distance = selected_route['AVERAGE_DISTANCE']
    average_time_minutes = selected_route['AVERAGE_TIME']
    
    st.info(f"📏 Distance: {distance} miles")
    st.info(f"⏱️ Average Flight Time: {average_time_minutes} minutes")

with col_map2:
    # Get coordinates for the map
    origin_coords = airports_df[airports_df['ID'] == origin_airport_id].iloc[0]
    dest_coords = airports_df[airports_df['ID'] == dest_airport_id].iloc[0]
    
    # Build data for PyDeck Map
    map_data = pd.DataFrame({
        "start_lat": [origin_coords['LATITUDE']],
        "start_lon": [origin_coords['LONGITUDE']],
        "end_lat": [dest_coords['LATITUDE']],
        "end_lon": [dest_coords['LONGITUDE']]
    })
    
    # Render an interactive 3D arc map
    st.pydeck_chart(pdk.Deck(
        map_style="dark",
        initial_view_state=pdk.ViewState(
            latitude=(origin_coords['LATITUDE'] + dest_coords['LATITUDE']) / 2,
            longitude=(origin_coords['LONGITUDE'] + dest_coords['LONGITUDE']) / 2,
            zoom=3,
            pitch=45,
        ),
        layers=[
            pdk.Layer(
                "ArcLayer",
                data=map_data,
                get_source_position=["start_lon", "start_lat"],
                get_target_position=["end_lon", "end_lat"],
                get_source_color=[200, 30, 0, 160],
                get_target_color=[0, 200, 30, 160],
                auto_highlight=True,
                width_scale=2,
                get_width=2,
            )
        ]
    ))

st.divider()

# --- SIDEBAR: FLIGHT INPUTS ---
st.sidebar.header("🛫 Flight Parameters")

selected_date = st.sidebar.date_input("Flight Date", datetime.date.today())
scheduled_departure_time = st.sidebar.time_input("Scheduled Departure Time", datetime.time(8, 30))

# Automatically calculate Arrival Time and Duration based on the Route Averages table
dep_datetime = datetime.datetime.combine(selected_date, scheduled_departure_time)
arr_datetime = dep_datetime + datetime.timedelta(minutes=average_time_minutes)

st.sidebar.info(f"🛬 Calculated Arrival: {arr_datetime.strftime('%H:%M')}")

flight_duration = average_time_minutes / 60.0
month = selected_date.month
day = selected_date.day
day_of_week = selected_date.weekday() 
scheduled_departure_int = (scheduled_departure_time.hour * 100) + scheduled_departure_time.minute
arrival_hour = arr_datetime.hour * 100

airline = st.sidebar.selectbox("Select Airline", options=list(airlines_dictionary.keys()), format_func=lambda x: airlines_dictionary[x])
airline_historic_delay = st.sidebar.number_input("Airline Historic Delay Rate", 0.0, 5.0, 1.0, 0.5)
route_historic_delay_by_airline = st.sidebar.number_input("Route Historic Delay Rate", 0.0, 5.0, 1.0, 0.5)
previous_flight_delayed_boolean = st.sidebar.checkbox("Previous Flight Delayed")
previous_flight_delayed = 1 if previous_flight_delayed_boolean else 0

st.sidebar.subheader("Weather & Traffic")
origin_weather_code = st.sidebar.number_input("Origin Weather Code (WMO)", 0, 100, 0)
origin_precipitation = st.sidebar.slider("Origin Precipitation (mm)", 0, 100, 50, 5)
origin_snowfall = st.sidebar.slider("Origin Snowfall (cm)", 0, 100, 50, 5)
origin_cloud_cover_low = st.sidebar.slider("Origin Fog (%)", 0, 100, 10, 5)
origin_temperature = st.sidebar.slider("Origin Temperature (°C)", -50, 50, 20, 5)
origin_surface_pressure = st.sidebar.slider("Origin Surface Pressure (Pa)", 1000, 1030, 1015, 1)
origin_hourly_airport_traffic = st.sidebar.slider("Origin Traffic", 0, 100, 20, 10)

dest_weather_code = st.sidebar.number_input("Destination Weather Code (WMO)", 0, 100, 0)
dest_precipitation = st.sidebar.slider("Destination Precipitation (mm)", 0, 100, 50, 5)
dest_snowfall = st.sidebar.slider("Destination Snowfall (cm)", 0, 100, 50, 5)
dest_cloud_cover_low = st.sidebar.slider("Destination Fog (%)", 0, 100, 10, 5)
dest_temperature = st.sidebar.slider("Destination Temperature (°C)", -50, 50, 20, 5)
dest_surface_pressure = st.sidebar.slider("Destination Surface Pressure (Pa)", 1000, 1030, 1015, 1)
des_hourly_airport_traffic = st.sidebar.slider("Destination Traffic", 0, 100, 20, 10)

payload = {
    "FLIGHT_DURATION_HOURS": flight_duration,  
    "MONTH": month,
    "DAY": day,
    "DAY_OF_WEEK": day_of_week,
    "AIRLINE_ID": airline,
    "ORIGIN_AIRPORT_ID": origin_airport_id,
    "DESTINATION_AIRPORT_ID": dest_airport_id,
    "DISTANCE": distance,
    "SCHEDULED_DEPARTURE_TIME": scheduled_departure_int,
    "ARRIVAL_HOUR": arrival_hour,
    "AIRLINE_HISTORIC_DELAY": airline_historic_delay,
    "ROUTE_HISTORIC_DELAY_BY_AIRLINE": route_historic_delay_by_airline,
    "ORIGIN_PRECIPITATION": origin_precipitation,
    "ORIGIN_SNOWFALL": origin_snowfall,
    "ORIGIN_CLOUD_COVER_LOW": origin_cloud_cover_low,
    "ORIGIN_TEMPERATURE": origin_temperature,
    "ORIGIN_SURFACE_PRESSURE": origin_surface_pressure,
    "ORIGIN_WEATHER_CODE": origin_weather_code,
    "DEST_PRECIPITATION": dest_precipitation,
    "DEST_SNOWFALL": dest_snowfall,
    "DEST_CLOUD_COVER_LOW": dest_cloud_cover_low,
    "DEST_TEMPERATURE": dest_temperature,
    "DEST_SURFACE_PRESSURE": dest_surface_pressure,
    "DEST_WEATHER_CODE": dest_weather_code,
    "PREVIOUS_FLIGHT_DELAYED": previous_flight_delayed,
    "ORIGIN_HOURLY_AIRPORT_TRAFFIC": origin_hourly_airport_traffic,
    "DEST_HOURLY_AIRPORT_TRAFFIC": des_hourly_airport_traffic,
}

# --- MAIN DASHBOARD AREA ---
if st.button("Run AI Analysis", type="primary", use_container_width=True):
    with st.spinner("Querying XGBoost and PuLP Engines..."):
        try:
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                status = result['flight_status']
                
                col1, col2, col3 = st.columns(3)
                
                if status == "On Time":
                    col1.metric(label="Predicted Status", value="✅ On Time")
                    col2.metric(label="Action Required", value="None")
                    col3.metric(label="Crew Cost Impact", value="$0")
                    st.success("The flight is cleared for an on-time departure. Standard crew remains assigned.")
                    
                else:
                    col1.metric(label="Predicted Status", value="🚨 Delayed")
                    col2.metric(label="Action Required", value="Standby Activated")
                    
                    opt_details = result.get('optimization_details', {})
                    if opt_details.get('Status') == 'Optimal': 
                        
                        cost = opt_details['Total_Hourly_Cost']
                        crew = opt_details['Selected_Crew']
                        
                        col3.metric(label="Optimized Crew Cost", value=f"${cost} / hr")
                        
                        st.warning("High risk of delay detected. Original crew is projected to time out.")
                        st.subheader("👨‍✈️ Prescriptive Crew Reassignment")
                        st.info(f"**Optimal Legal Crew Found:** {', '.join(crew)}")
                        st.markdown("This combination minimizes financial impact while satisfying FAA staffing limits and available standby hours.")
                    else:
                        col3.metric(label="Optimized Crew Cost", value="ERROR")
                        error_msg = opt_details.get('Message', 'Not enough legal hours remaining in the standby pool to cover this flight.')
                        st.error(f"Delay detected, but optimization failed: {error_msg}")
                        
            elif response.status_code == 422:
                st.error("Schema Error: The frontend inputs do not match the FastAPI Pydantic requirements. Check your variable names and types.")
                st.json(response.json())
            else:
                st.error(f"Server Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the FastAPI backend. Ensure `uvicorn main:app --reload` is running in another terminal.")