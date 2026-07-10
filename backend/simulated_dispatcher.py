import os
from dotenv import load_dotenv
import time
import requests
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()
print("Connecting to PostgreSQL...")

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(db_url)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/check_flight")

def run_simulation():
    batch_size = 10
    offset = 0
    batch_num = 1
    
    while True:
        print(f"\nFetching Batch #{batch_num} (Offset: {offset})...")
        
        # Added OFFSET to skip the rows we have already processed
        query = f"""
            SELECT * FROM public.model_features_v08
            ORDER BY "MONTH" ASC, "DAY" ASC, "SCHEDULED_DEPARTURE_TIME" ASC
            LIMIT {batch_size} OFFSET {offset};
        """
        flights_df = pd.read_sql(query, engine)
        
        # If the query returns an empty dataframe, we reached the end of the dataset
        if flights_df.empty:
            print("No more flights found in the database. Simulation complete!")
            break
            
        print(f"Loaded {len(flights_df)} flights. Starting real-time simulation...\n")
        print("-" * 50)
        
        for index, row in flights_df.iterrows():
            flight_data = row.to_dict()
            
            if 'FLIGHT_DURATION_HOURS' not in flight_data:
                flight_data['FLIGHT_DURATION_HOURS'] = 6.5 
            
            # Calculate the true flight number across batches
            global_flight_num = offset + index + 1
            print(f"[{time.strftime('%H:%M:%S')}] Checking Flight #{global_flight_num}...")
            
            try:
                response = requests.post(API_URL, json=flight_data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  -> Status: {result['flight_status']}")
                    print(f"  -> Action: {result['action']}")
                    
                    if 'optimization_details' in result:
                        # Catch if the solver failed (e.g. not enough crew hours)
                        if result['optimization_details'].get('Status') != 'Optimal':
                            print(f"  -> Optimization Failed: {result['optimization_details'].get('Message', 'No valid crew.')}")
                        else:
                            print(f"  -> Crew Dispatched: {result['optimization_details']['Selected_Crew']}")
                            print(f"  -> Estimated Cost: ${result['optimization_details']['Total_Hourly_Cost']}")
                else:
                    print(f"  -> API Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print("  -> Failed to connect to API. Is Uvicorn running?")
                return # Kills the loop so it doesn't endlessly error out
                
            print("-" * 50)
            time.sleep(5)
            
        # Increment the offset and batch number for the next loop iteration
        offset += batch_size
        batch_num += 1

if __name__ == "__main__":
    run_simulation()