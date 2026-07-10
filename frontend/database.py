import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource 
def init_connection():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(db_url)

@st.cache_data 
def fetch_airlines():
    query = 'SELECT "ID", "AIRLINE" FROM public.airlines;' 
    df = pd.read_sql(query, init_connection())
    return dict(zip(df['ID'], df['AIRLINE']))

@st.cache_data
def fetch_airports():
    query = 'SELECT "ID", "AIRPORT", "LATITUDE", "LONGITUDE" FROM public.airports;' 
    return pd.read_sql(query, init_connection())

@st.cache_data
def fetch_routes():
    # Note: Enforced double quotes on ROUTE_AVERAGES to match your SQL creation script
    query = 'SELECT "ORIGIN_AIRPORT_ID", "ARRIVAL_AIRPORT_ID", "AVERAGE_DISTANCE", "AVERAGE_TIME" FROM public.route_averages;'
    return pd.read_sql(query, init_connection())