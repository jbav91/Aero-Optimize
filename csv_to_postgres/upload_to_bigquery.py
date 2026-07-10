import os
from google.cloud import bigquery

# 1. Securely set your Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-key.json"

def upload_full_flights_to_bigquery():
    # 2. Initialize the BigQuery Client
    client = bigquery.Client()

    # --- UPDATE THESE VARIABLES ---
    project_id = "aero-optimize"  # e.g., "aero-optimize-12345"
    dataset_id = "flight_data"          
    table_id = f"{project_id}.{dataset_id}.raw_flights_2015"
    file_path = "dataset/flights.csv"   # Updated to your target folder
    # ------------------------------

    # 3. Create the dataset in BigQuery (if it doesn't exist)
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = "US" 
    dataset = client.create_dataset(dataset_ref, exists_ok=True)
    print(f"Dataset {dataset.dataset_id} created or verified.")

    # 4. Configure the BigQuery load job for a direct CSV upload
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,          # Skips the CSV header row
        autodetect=True,              # Automatically infers SQL data types (INTEGER, STRING, etc.)
        write_disposition="WRITE_TRUNCATE", # Overwrites the table if run multiple times
    )

    # 5. Stream the full file directly to Google Cloud
    print(f"Uploading entire dataset from {file_path} to BigQuery...")
    print("This may take a few minutes depending on your internet upload speed.")
    
    with open(file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)
    
    # 6. Wait for the job to complete and verify
    job.result() 
    
    # Fetch the table to confirm the exact row count
    table = client.get_table(table_id)
    print(f"Success! Uploaded {table.num_rows} rows to {table_id}")

if __name__ == "__main__":
    upload_full_flights_to_bigquery()