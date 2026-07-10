import pandas as pd

# 1. Load the two reference dictionaries
df_iata = pd.read_csv('dataset/L_AIRPORT.csv')
df_iata.rename(columns={'Code': 'IATA_CODE'}, inplace=True)

df_numeric = pd.read_csv('dataset/L_AIRPORT_ID.csv')
df_numeric.rename(columns={'Code': 'NUMERIC_CODE'}, inplace=True)

# 2. Merge them on 'Description' to create the mapping
crosswalk = pd.merge(df_iata, df_numeric, on='Description', how='inner')
crosswalk.drop_duplicates(subset=['IATA_CODE'], inplace=True)

# 3. Load your main airports dataset
airports_df = pd.read_csv('dataset/airports.csv')

# 4. Merge the numeric code into your airports dataset
updated_airports = pd.merge(airports_df, crosswalk[['IATA_CODE', 'NUMERIC_CODE']], on='IATA_CODE', how='left')

# 5. Rename to 'code' as requested and save
updated_airports.rename(columns={'NUMERIC_CODE': 'CODE'}, inplace=True)
updated_airports.to_csv('dataset/airports_updated.csv', index=False)

print("Success! Numeric codes appended. Saved to dataset/airports_updated.csv")
print(updated_airports.head())