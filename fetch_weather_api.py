import requests
import pandas as pd
import time

def build_hourly_weather_dataset():
    print("Loading airports list...")
    # 1. Load the airports dynamically from the CSV
    airports_df = pd.read_csv('dataset/airports.csv')
    
    # Optional: Drop any rows that might be missing coordinates just to be safe
    airports_df = airports_df.dropna(subset=['LATITUDE', 'LONGITUDE'])
    
    all_weather_chunks = []
    total_airports = len(airports_df)
    
    print(f"Fetching 2015 hourly weather for {total_airports} airports. This will take ~6 minutes...")

    # 2. Loop through every airport in the file
    for index, row in airports_df.iterrows():
        airport_code = row['IATA_CODE']
        lat = row['LATITUDE']
        lon = row['LONGITUDE']
        
        print(f"[{index + 1}/{total_airports}] Fetching {airport_code}...")
        
        # 3. Open-Meteo Hourly API Endpoint
        url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={lat}&longitude={lon}"
            f"&start_date=2015-01-01&end_date=2015-12-31"
            f"&hourly=precipitation,snowfall" # Changed to hourly
            f"&timezone=America/New_York"
        )
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # 4. Create a temporary DataFrame for this specific airport to process it quickly
            temp_df = pd.DataFrame({
                'AIRPORT_CODE': airport_code,
                'TIME': pd.to_datetime(data['hourly']['time']),
                'PRECIPITATION': data['hourly']['precipitation'],
                'SNOWFALL': data['hourly']['snowfall']
            })
            
            # Extract Month, Day, and Hour so we can easily join it to the flight dataset later
            temp_df['MONTH'] = temp_df['TIME'].dt.month
            temp_df['DAY'] = temp_df['TIME'].dt.day
            temp_df['HOUR'] = temp_df['TIME'].dt.hour
            
            # Drop the raw timestamp column to save memory
            temp_df = temp_df.drop(columns=['TIME'])
            
            all_weather_chunks.append(temp_df)
        else:
            print(f"  -> Failed to fetch {airport_code}. Status: {response.status_code}")
            
        # 5. VERY IMPORTANT: Pause for 1 second so the API doesn't ban us
        time.sleep(1)

    # 6. Combine all 323 mini-dataframes into one massive dataframe
    print("\nCombining data...")
    final_df = pd.concat(all_weather_chunks, ignore_index=True)
    
    output_path = "dataset/hourly_weather_2015.csv"
    final_df.to_csv(output_path, index=False)
    
    print(f"Success! {len(final_df):,} rows of hourly weather saved to {output_path}")

if __name__ == "__main__":
    build_hourly_weather_dataset()