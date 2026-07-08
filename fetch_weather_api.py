import requests
import pandas as pd
import time

def build_hourly_weather_dataset():
    print("Loading airports list...")
    airports_df = pd.read_csv('dataset/airports_updated.csv')
    airports_df = airports_df.dropna(subset=['LATITUDE', 'LONGITUDE'])
    
    all_weather_chunks = []
    total_airports = len(airports_df)
    
    print(f"Fetching 2015 hourly weather for {total_airports} airports...")

    for index, row in airports_df.iterrows():
        airport_code = row['IATA_CODE']
        lat = row['LATITUDE']
        lon = row['LONGITUDE']
        
        print(f"[{index + 1}/{total_airports}] Fetching {airport_code}...")
        
        url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={lat}&longitude={lon}"
            f"&start_date=2015-01-01&end_date=2015-12-31"
            f"&hourly=precipitation,snowfall,wind_speed_10m,wind_gusts_10m,cloud_cover_low,weather_code,temperature_2m,surface_pressure"
            f"&timezone=America/New_York"
        )
        
        # --- THE NEW RESILIENT RETRY LOGIC ---
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                temp_df = pd.DataFrame({
                    'AIRPORT_CODE': airport_code,
                    'TIME': pd.to_datetime(data['hourly']['time']),
                    'PRECIPITATION': data['hourly']['precipitation'],
                    'SNOWFALL': data['hourly']['snowfall'],
                    'WIND_SPEED': data['hourly']['wind_speed_10m'],
                    'WIND_GUSTS': data['hourly']['wind_gusts_10m'],
                    'CLOUD_COVER_LOW': data['hourly']['cloud_cover_low'],
                    'WEATHER_CODE': data['hourly']['weather_code'], 
                    'TEMPERATURE_2M': data['hourly']['temperature_2m'], 
                    'SURFACE_PRESSURE': data['hourly']['surface_pressure'], 
                })
                
                temp_df['MONTH'] = temp_df['TIME'].dt.month
                temp_df['DAY'] = temp_df['TIME'].dt.day
                temp_df['HOUR'] = temp_df['TIME'].dt.hour
                temp_df = temp_df.drop(columns=['TIME'])
                
                all_weather_chunks.append(temp_df)
                break # Success! Break out of the retry loop and move to the next airport
                
            elif response.status_code == 429:
                print(f"  -> Rate limited (429)! API needs a breather. Pausing for 60 seconds... (Attempt {attempt + 1} of {max_retries})")
                time.sleep(60) # Wait a full minute before trying this airport again
                
            else:
                print(f"  -> Failed to fetch {airport_code}. Status: {response.status_code}")
                break # If it's a 404 or 500 error, waiting won't help. Move on.
                
        # Standard safety pause between successful requests
        time.sleep(2)

    print("\nCombining data...")
    if len(all_weather_chunks) > 0:
        final_df = pd.concat(all_weather_chunks, ignore_index=True)
        output_path = "dataset/hourly_weather_2015.csv"
        final_df.to_csv(output_path, index=False)
        print(f"Success! {len(final_df):,} rows of hourly weather saved to {output_path}")
    else:
        print("No data was fetched. Check your API limits.")

if __name__ == "__main__":
    build_hourly_weather_dataset()