import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

def upload_full_flights_to_postgres():
    # 1. Load the variables from the .env file into the system
    load_dotenv()

    # 2. Securely fetch the credentials
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    # 3. Construct the database URL dynamically
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    
    file_path = "dataset/hourly_weather_2015.csv"
    print(f"Reading data from {file_path} and auto-generating table schema...")
    
    chunksize = 10000 
    first_chunk = True
    
    with pd.read_csv(file_path, chunksize=chunksize, low_memory=False) as reader:
        for i, chunk in enumerate(reader):
            print(f"Uploading chunk {i + 1}...")
            
            if first_chunk:
                # Creates the brand new 31-column table
                chunk.to_sql('raw_weather_2015', engine, if_exists='replace', index=False)
                first_chunk = False
            else:
                # Appends to the table
                chunk.to_sql('raw_weather_2015', engine, if_exists='append', index=False)
            
    print("Success! Table automatically created and all data loaded securely.")

if __name__ == "__main__":
    upload_full_flights_to_postgres()