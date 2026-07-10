import streamlit as st
import datetime

def render_sidebar(airlines_dictionary, average_time_minutes):
    """Renders the sidebar UI and returns a dictionary of the selected values."""
    st.sidebar.header("🛫 Flight Parameters")
    
    selected_date = st.sidebar.date_input("Flight Date", datetime.date.today())
    scheduled_departure_time = st.sidebar.time_input("Scheduled Departure Time", datetime.time(8, 30))

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
    previous_flight_delayed = 1 if st.sidebar.checkbox("Previous Flight Delayed") else 0

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

    # Package all sidebar variables into a dictionary to return to main.py
    return {
        "FLIGHT_DURATION_HOURS": flight_duration, "MONTH": month, "DAY": day, "DAY_OF_WEEK": day_of_week,
        "AIRLINE_ID": airline, "SCHEDULED_DEPARTURE_TIME": scheduled_departure_int, "ARRIVAL_HOUR": arrival_hour,
        "AIRLINE_HISTORIC_DELAY": airline_historic_delay, "ROUTE_HISTORIC_DELAY_BY_AIRLINE": route_historic_delay_by_airline,
        "ORIGIN_PRECIPITATION": origin_precipitation, "ORIGIN_SNOWFALL": origin_snowfall, "ORIGIN_CLOUD_COVER_LOW": origin_cloud_cover_low,
        "ORIGIN_TEMPERATURE": origin_temperature, "ORIGIN_SURFACE_PRESSURE": origin_surface_pressure, "ORIGIN_WEATHER_CODE": origin_weather_code,
        "DEST_PRECIPITATION": dest_precipitation, "DEST_SNOWFALL": dest_snowfall, "DEST_CLOUD_COVER_LOW": dest_cloud_cover_low,
        "DEST_TEMPERATURE": dest_temperature, "DEST_SURFACE_PRESSURE": dest_surface_pressure, "DEST_WEATHER_CODE": dest_weather_code,
        "PREVIOUS_FLIGHT_DELAYED": previous_flight_delayed, "ORIGIN_HOURLY_AIRPORT_TRAFFIC": origin_hourly_airport_traffic,
        "DEST_HOURLY_AIRPORT_TRAFFIC": des_hourly_airport_traffic,
    }