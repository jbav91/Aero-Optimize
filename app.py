import streamlit as st
import requests
import pandas as pd
import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

# Setup the database connection function and CACHE it
@st.cache_resource # Caches the connection engine itself
def init_connection():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    # Don't forget urllib.parse.quote_plus if your password has special characters!
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(db_url)

# Setup the data fetching function and CACHE the results
@st.cache_data # Caches the actual data so it doesn't query the DB on every click
def fetch_airlines():
    engine = init_connection()
    query = "SELECT * FROM public.airlines;" 
    
    df = pd.read_sql(query, engine)
    
    # Convert the two columns into a Python dictionary: { 1: "Delta", 2: "United", ... }
    return dict(zip(df['ID'], df['AIRLINE']))
def fetch_airports():
    engine = init_connection()
    query = "SELECT * FROM public.airports;" 
    
    df = pd.read_sql(query, engine)
    
    # Convert the two columns into a Python dictionary: { 1: "Delta", 2: "United", ... }
    return dict(zip(df['ID'], df['AIRPORT']))

# --- UI IMPLEMENTATION ---

# Fetch the dynamic dictionary (this happens instantly from cache after the first load)
airlines_dictionary = fetch_airlines()
airports_dictionary = fetch_airports()

# --- CONFIGURATION ---
st.set_page_config(page_title="Aero-Optimize AI", page_icon="✈️", layout="wide")
API_URL = "http://127.0.0.1:8000/api/check_flight"

# --- UI HEADER ---
st.title("✈️ Aero-Optimize: Smart Dispatch System")
st.markdown("Predict flight delays and mathematically optimize standby crew assignments in real-time.")
st.divider()

# --- SIDEBAR: FLIGHT INPUTS ---
st.sidebar.header("🛫 Flight Parameters")
st.sidebar.markdown("Input the pre-flight conditions below:")

# Use a calendar widget to get the Date and Hours
selected_date = st.sidebar.date_input("Flight Date", datetime.date.today())
scheduled_departure_time = st.sidebar.time_input("Scheduled Departure Time", datetime.time(8, 30))
scheduled_arrival_time = st.sidebar.time_input("Scheduled Arrival Time", datetime.time(8, 30))
previous_flight_delayed_boolean = st.sidebar.checkbox("Previous Flight Delayed")

# Parameters
# Calculate Flight Duration
# Combine the date and times into full datetime objects so Python can do math
dep_datetime = datetime.datetime.combine(selected_date, scheduled_departure_time)
arr_datetime = datetime.datetime.combine(selected_date, scheduled_arrival_time)
# Handle overnight flights (if arrival time is mathematically earlier than departure time)
if arr_datetime < dep_datetime:
    arr_datetime += datetime.timedelta(days=1)
# Subtract to get the difference, then convert to hours as a float
duration_delta = arr_datetime - dep_datetime

flight_duration = duration_delta.total_seconds() / 3600.0
month = selected_date.month
day = selected_date.day
day_of_week = selected_date.weekday() # 0 = Monday, 6 = Sunday
airline_historic_delay = st.sidebar.number_input("Airline Historic Delay Rate", 0.0, 5.0, 1.0, 0.5)
route_historic_delay_by_airline = st.sidebar.number_input("Route Historic Delay Rate", 0.0, 5.0, 1.0, 0.5)
origin_weather_code = st.sidebar.number_input("Origin Weather Code (WMO)", 0, 100, 0)
airline = st.sidebar.selectbox("Select Airline", options=list(airlines_dictionary.keys()), format_func=lambda x: airlines_dictionary[x])
origin_airport = st.sidebar.selectbox("Origin Airport", options=list(airports_dictionary.keys()), format_func=lambda x: airports_dictionary[x])
dest_airport = st.sidebar.selectbox("Destination Airport", options=list(airports_dictionary.keys()), format_func=lambda x: airports_dictionary[x])
distance = st.sidebar.slider("Distance (km)", 0, 5000, 500, 100)
scheduled_departure_int = (scheduled_departure_time.hour * 100) + scheduled_departure_time.minute
arrival_hour = scheduled_arrival_time.hour * 100
origin_precipitation = st.sidebar.slider("Origin Precipitation (mm)", 0, 100, 50, 5)
origin_snowfall = st.sidebar.slider("Origin Snowfall (cm)", 0, 100, 50, 5)
origin_cloud_cover_low = st.sidebar.slider("Origin Fog (%)", 0, 100, 10, 5)
origin_temperature = st.sidebar.slider("Origin Temperature (°C)", -50, 50, 20, 5)
origin_surface_pressure = st.sidebar.slider("Origin Surface Pressure (Pa)", 1000, 1030, 1015, 1)
dest_precipitation = st.sidebar.slider("Destination Precipitation (mm)", 0, 100, 50, 5)
dest_snowfall = st.sidebar.slider("Destination Snowfall (cm)", 0, 100, 50, 5)
dest_cloud_cover_low = st.sidebar.slider("Destination Fog (%)", 0, 100, 10, 5)
dest_temperature = st.sidebar.slider("Destination Temperature (°C)", -50, 50, 20, 5)
dest_surface_pressure = st.sidebar.slider("Destination Surface Pressure (Pa)", 1000, 1030, 1015, 1)
dest_weather_code = st.sidebar.number_input("Destination Weather Code (WMO)", 0, 100, 0)
previous_flight_delayed = 1 if previous_flight_delayed_boolean else 0
origin_hourly_airport_traffic = st.sidebar.slider("Origin Traffic", 0, 100, 20, 10)
des_hourly_airport_traffic = st.sidebar.slider("Destination Traffic", 0, 100, 20, 10)

# Package into dictionary
payload = {
    "FLIGHT_DURATION_HOURS": flight_duration,  # Required for the PuLP solver
    "MONTH": month,
    "DAY": day,
    "DAY_OF_WEEK": day_of_week,
    "AIRLINE_ID": airline,
    "ORIGIN_AIRPORT_ID": origin_airport,
    "DESTINATION_AIRPORT_ID": dest_airport,
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
if st.sidebar.button("Run AI Analysis", type="primary", use_container_width=True):
    with st.spinner("Querying XGBoost and PuLP Engines..."):
        try:
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                status = result['flight_status']
                
                # Top Row: Metrics
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
                        
                        # 2. Update these keys to match your Day 3 output exactly
                        cost = opt_details['Total_Hourly_Cost']
                        crew = opt_details['Selected_Crew']
                        
                        col3.metric(label="Optimized Crew Cost", value=f"${cost} / hr")
                        
                        st.warning("High risk of delay detected. Original crew is projected to time out.")
                        
                        st.subheader("👨‍✈️ Prescriptive Crew Reassignment")
                        st.info(f"**Optimal Legal Crew Found:** {', '.join(crew)}")
                        
                        st.markdown("This combination minimizes financial impact while satisfying FAA staffing limits and available standby hours.")
                    else:
                        col3.metric(label="Optimized Crew Cost", value="ERROR")
                        # 3. Update 'Message' key (if you have one) or provide fallback
                        error_msg = opt_details.get('Message', 'Not enough legal hours remaining in the standby pool to cover this flight.')
                        st.error(f"Delay detected, but optimization failed: {error_msg}")
                        
            elif response.status_code == 422:
                st.error("Schema Error: The frontend inputs do not match the FastAPI Pydantic requirements. Check your variable names and types.")
                st.json(response.json())
            else:
                st.error(f"Server Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the FastAPI backend. Ensure `uvicorn main:app --reload` is running in another terminal.")
else:
    # Default landing screen
    st.info("👈 Enter flight parameters in the sidebar and click 'Run AI Analysis' to test the system.")