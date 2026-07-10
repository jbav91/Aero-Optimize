from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib

# Import your Day 3 optimization function
from assign_standby_crew import assign_standby_crew

# ---------------------------------------------------------
# 1. INITIALIZE THE API
# ---------------------------------------------------------
app = FastAPI(title="Flight Optimization & Crew API", version="1.0")

# ---------------------------------------------------------
# 2. LOAD THE PREDICTIVE ASSET (XGBoost)
# ---------------------------------------------------------
print("Booting up: Loading XGBoost Champion Model...")
try:
    model = joblib.load('model_xgboost_v08_v01.joblib')
    print("Success: Brain loaded into memory.")
except FileNotFoundError:
    print("Error: Model file not found. Make sure 'xgboost_delay_model_v06.joblib' is in this directory.")
    model = None

# ---------------------------------------------------------
# 3. DEFINE THE INCOMING DATA FORMAT (Pydantic Schema)
# ---------------------------------------------------------
# IMPORTANT: You must update these fields to perfectly match the 
# features your XGBoost model was trained on!
class FlightData(BaseModel):
    FLIGHT_DURATION_HOURS: float  # Required for the PuLP solver
    # --- ML Features below ---
    MONTH: int
    DAY: int
    DAY_OF_WEEK: int
    AIRLINE_ID: int
    ORIGIN_AIRPORT_ID: int
    DESTINATION_AIRPORT_ID: int
    DISTANCE: int
    SCHEDULED_DEPARTURE_TIME: int
    ARRIVAL_HOUR: int
    AIRLINE_HISTORIC_DELAY: float
    ROUTE_HISTORIC_DELAY_BY_AIRLINE: float
    ORIGIN_PRECIPITATION: float
    ORIGIN_SNOWFALL: float
    ORIGIN_CLOUD_COVER_LOW: float
    ORIGIN_TEMPERATURE: float
    ORIGIN_SURFACE_PRESSURE: float
    ORIGIN_WEATHER_CODE: int
    DEST_PRECIPITATION: float
    DEST_SNOWFALL: float
    DEST_CLOUD_COVER_LOW: float
    DEST_TEMPERATURE: float
    DEST_SURFACE_PRESSURE: float
    DEST_WEATHER_CODE: int
    PREVIOUS_FLIGHT_DELAYED: int
    ORIGIN_HOURLY_AIRPORT_TRAFFIC: int
    DEST_HOURLY_AIRPORT_TRAFFIC: int
    # ... add the rest of your features here

# ---------------------------------------------------------
# 4. BASIC HEALTH CHECK ENDPOINT
# ---------------------------------------------------------
@app.get("/")
def read_root():
    return {"message": "Flight API is online and ready."}

# ---------------------------------------------------------
# 5. THE MASTER PIPELINE (Predictive -> Prescriptive)
# ---------------------------------------------------------
@app.post("/api/check_flight")
def check_flight(flight: FlightData):
    if model is None:
        raise HTTPException(status_code=500, detail="XGBoost model is offline.")

    # 1. Package the incoming JSON into a DataFrame for XGBoost
    # Ensure the dictionary keys exactly match your training column names
    input_data = pd.DataFrame([{
        'MONTH': flight.MONTH,
        'DAY': flight.DAY,
        'DAY_OF_WEEK': flight.DAY_OF_WEEK,
        'AIRLINE_ID': flight.AIRLINE_ID,
        'ORIGIN_AIRPORT_ID': flight.ORIGIN_AIRPORT_ID,
        'DESTINATION_AIRPORT_ID': flight.DESTINATION_AIRPORT_ID,
        'DISTANCE': flight.DISTANCE,
        'SCHEDULED_DEPARTURE_TIME': flight.SCHEDULED_DEPARTURE_TIME,
        'ARRIVAL_HOUR': flight.ARRIVAL_HOUR,
        'AIRLINE_HISTORIC_DELAY': flight.AIRLINE_HISTORIC_DELAY,
        'ROUTE_HISTORIC_DELAY_BY_AIRLINE': flight.ROUTE_HISTORIC_DELAY_BY_AIRLINE,
        'ORIGIN_PRECIPITATION': flight.ORIGIN_PRECIPITATION,
        'ORIGIN_SNOWFALL': flight.ORIGIN_SNOWFALL,
        'ORIGIN_CLOUD_COVER_LOW': flight.ORIGIN_CLOUD_COVER_LOW,
        'ORIGIN_TEMPERATURE': flight.ORIGIN_TEMPERATURE,
        'ORIGIN_SURFACE_PRESSURE': flight.ORIGIN_SURFACE_PRESSURE,
        'ORIGIN_WEATHER_CODE': flight.ORIGIN_WEATHER_CODE,
        'DEST_PRECIPITATION': flight.DEST_PRECIPITATION,
        'DEST_SNOWFALL': flight.DEST_SNOWFALL,
        'DEST_CLOUD_COVER_LOW': flight.DEST_CLOUD_COVER_LOW,
        'DEST_TEMPERATURE': flight.DEST_TEMPERATURE,
        'DEST_SURFACE_PRESSURE': flight.DEST_SURFACE_PRESSURE,
        'DEST_WEATHER_CODE': flight.DEST_WEATHER_CODE,
        'PREVIOUS_FLIGHT_DELAYED': flight.PREVIOUS_FLIGHT_DELAYED,
        'ORIGIN_HOURLY_AIRPORT_TRAFFIC': flight.ORIGIN_HOURLY_AIRPORT_TRAFFIC,
        'DEST_HOURLY_AIRPORT_TRAFFIC': flight.DEST_HOURLY_AIRPORT_TRAFFIC,
        # ... add the rest here
    }])

    # 2. The Predictive Trigger
    # predict() returns an array like [0] or [1]. We grab the first item.
    prediction = int(model.predict(input_data)[0])

    # 3. The Handoff & Prescriptive Response
    if prediction == 0:
        return {
            "flight_status": "On Time",
            "prediction_code": prediction,
            "action": "None required."
        }
    else:
        # It's delayed! Run the PuLP solver using the required flight duration.
        optimization_result = assign_standby_crew(flight.FLIGHT_DURATION_HOURS)

        return {
            "flight_status": "Delayed",
            "prediction_code": prediction,
            "action": "Standby crew activated.",
            "optimization_details": optimization_result
        }