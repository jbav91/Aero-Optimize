import pandas as pd
from sqlalchemy import create_engine
from dotenv import dotenv_values

# 1. Setup Connections (Replace with your actual passwords and Neon URL)

# 1. Load environments into isolated dictionaries to prevent variable collision
local_env = dotenv_values(".env")
prod_env = dotenv_values(".env.prod")

# 2. Build the connection strings dynamically
local_db_url = f"postgresql://{local_env['DB_USER']}:{local_env['DB_PASSWORD']}@{local_env['DB_HOST']}:{local_env['DB_PORT']}/{local_env['DB_NAME']}"
neon_db_url = f"postgresql://{prod_env['DB_USER']}:{prod_env['DB_PASSWORD']}@{prod_env['DB_HOST']}:{prod_env['DB_PORT']}/{prod_env['DB_NAME']}?sslmode=require"

local_engine = create_engine(local_db_url)
neon_engine = create_engine(neon_db_url)

# 2. List the tables you want to move one by one
# IMPORTANT: Ensure the spelling and capitalization perfectly match your local DB
tables_to_migrate = [
    "airlines", 
    "airports", 
    "route_averages"
]

# 3. Execute the transfer table by table
for table_name in tables_to_migrate:
    print(f"Fetching '{table_name}' from local database...")
    
    # Read the data from your local machine into RAM
    # We wrap the table name in double quotes to handle case-sensitivity (like ROUTE_AVERAGES)
    df = pd.read_sql(f'SELECT * FROM public."{table_name}"', local_engine)
    
    print(f"Found {len(df)} rows. Pushing to Neon...")
    
    # Write the data directly to the cloud
    # if_exists='replace' tells Pandas to automatically create the table in Neon
    df.to_sql(name=table_name, con=neon_engine, schema='public', if_exists='replace', index=False)
    
    print(f"✅ Successfully migrated '{table_name}'!\n")

print("🎉 All tables successfully copied to the cloud!")