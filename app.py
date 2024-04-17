# -*- coding: utf-8 -*-

"""
Energy Solar Generation: web app that
predicts solar power using OpenMeteo API.
Author: Andres Felipe Forero Correa
Date: 2023-08-25
"""
import sys
import os
import datetime as dt
import json
import plotly.express as px
import streamlit as st
from modules.functions import \
    fetch_json, get_weather_df_from_open_meteo_json, \
    create_csv_download_link, create_excel_download_link

# Constants
custom_location_name = "personalizado"
forecast_days = 7
min_date = dt.date.today() + dt.timedelta(days=1)
max_date = min_date + dt.timedelta(days=forecast_days-1)
mega = 10e6
kilo = 10e3
color_palettes = [px.colors.qualitative.Plotly, px.colors.qualitative.Dark24]
color_palette = px.colors.qualitative.Plotly

#weather_variables = ["direct_radiation", "direct_radiation_instant", "direct_normal_irradiance", "direct_normal_irradiance_instant"]
weather_variables = ["direct_radiation"]
weather_variables_str = (",").join(weather_variables)

OPEN_METEO_API_URL_TEMPLATE = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly={weather_variables_str}&timezone={timezone}"

if __name__ == "__main__":
    # URL template: http://localhost:8501/?latitude=4.14924&longitude=-74.88429&area=100&start_date=2024-04-17&end_date=2024-04-24&timezone=America/Bogota
    
    # Extract params from URL
    params = st.query_params   
    latitude = params.get('latitude', '')
    longitude = params.get('longitude', '')
    area = params.get('area', '')
    start_date = params.get('start_date', '')
    end_date = params.get('end_date', '')
    timezone = params.get('timezone', '')
    
    # Test input params
    # st.success(f"latitude: {latitude}")
    # st.success(f"longitude: {longitude}")
    # st.success(f"area: {area}")
    # st.success(f"start_date: {start_date}")
    # st.success(f"end_date: {end_date}")
    # st.success(f"timezone: {timezone}")

    # Format the OPEN_METEO_URL_TEMPLATE
    open_meteo_api_url = OPEN_METEO_API_URL_TEMPLATE.format(latitude=latitude, longitude=longitude, area=area, start_date=start_date, end_date=end_date, weather_variables_str=weather_variables_str, timezone=timezone)
    
    # Test API URL
    #st.success(open_meteo_api_url)
    json_data = fetch_json(open_meteo_api_url)
    
    # Forecast dataframe from JSON data
    forecast_df = get_weather_df_from_open_meteo_json(json_data)
    forecast_df = forecast_df.set_index('datetime')
    
    # Convert weather variable columns from Watts to kilo Watts
    for w_variable in weather_variables:
        forecast_df[f"{w_variable} [kW/m²]"] = forecast_df[f"{w_variable} [W/m²]"] / kilo
    
    # Delete old columns
    columns_will_be_delete = []
    for w_variable in weather_variables:
        columns_will_be_delete.append(f"{w_variable} [W/m²]")
    forecast_df = forecast_df.drop(columns=columns_will_be_delete)

    # Obtain power generation from each weather variable
    for w_variable in weather_variables:
        forecast_df[f"power_from_{w_variable} [kW]"] = forecast_df[f"{w_variable} [kW/m²]"] * float(area)
    
    # Show output dataframe
    st.header('Dataframe de predicción')
    st.dataframe(forecast_df)
