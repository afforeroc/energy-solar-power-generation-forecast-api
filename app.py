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

main_weather_variable_en = "direct_radiation"
main_weather_variable_es = "radiacion_directa"
#weather_variables = ["direct_radiation", "direct_radiation_instant", "direct_normal_irradiance", "direct_normal_irradiance_instant"]
#weather_variables_str = (",").join(weather_variables)

OPEN_METEO_API_URL_TEMPLATE = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly={weather_variables_str}&timezone={timezone}"

if __name__ == "__main__":
    # URL template: http://localhost:8501/?latitude=4.14924&longitude=-74.88429&area=100&start_date=2024-04-17&end_date=2024-04-24&timezone=America/Bogota
    
    # Page title, title and caption of the web app
    st.set_page_config(page_title="DERMS: Predicción de energía solar", page_icon="🌞")
    st.title("Predicción de Energía Solar")
    st.caption("Sistema de predicción de generación de energía solar de Energy Computer Systems")

    # Extract params from URL
    params = st.query_params   
    latitude = params.get('latitude', '')
    longitude = params.get('longitude', '')
    area = params.get('area', '')
    start_date = params.get('start_date', '')
    end_date = params.get('end_date', '')
    timezone = params.get('timezone', '')
    latitude = st.text_input("Latitud", latitude)
    longitude = st.text_input("Longitud", longitude)
    area = st.text_input("Área", area)
    start_date = st.date_input("Fecha inicial", value=dt.datetime.strptime(start_date, "%Y-%m-%d"))
    end_date = st.date_input("Fecha final", value=dt.datetime.strptime(end_date, "%Y-%m-%d"))

    # Format the OPEN_METEO_URL_TEMPLATE
    open_meteo_api_url = OPEN_METEO_API_URL_TEMPLATE.format(latitude=latitude, longitude=longitude, area=area, start_date=start_date, end_date=end_date, weather_variables_str=main_weather_variable_en, timezone=timezone)
    
    # Test API URL
    st.header('Test Open Meteo API URL')
    st.success(open_meteo_api_url)
    json_data = fetch_json(open_meteo_api_url)
    
    # Forecast dataframe from JSON data
    forecast_df = get_weather_df_from_open_meteo_json(json_data)
    forecast_df = forecast_df.rename(columns={"datetime": "fecha_hora"})
    forecast_df = forecast_df.set_index("fecha_hora")
    
    # Convert weather variable columns from Watts to kilo Watts
    forecast_df[f"{main_weather_variable_es} [kW/m²]"] = forecast_df[f"{main_weather_variable_en} [W/m²]"] / kilo
    
    # Delete old column
    forecast_df = forecast_df.drop(columns=[f"{main_weather_variable_en} [W/m²]"])

    # Obtain solar power generation from main weather variable
    forecast_df[f"potencia_solar [kW]"] = forecast_df[f"{main_weather_variable_es} [kW/m²]"] * float(area)
    
    # Show output dataframe
    st.header('Dataframe de predicción')
    st.dataframe(forecast_df)

    # Download in excel
    output_filename = f"prediccion_solar_lat{latitude}_lon{longitude}_area{area}"
    excel_filename = output_filename + ".xlsx"
    download_excel_link = create_excel_download_link(forecast_df.reset_index(), excel_filename, "Descargar Excel")
    st.markdown(download_excel_link, unsafe_allow_html=True)

    # First graph: Solar power of all days
    st.header("Curvas de predicción de todos los días")
    graph_df = forecast_df.reset_index().copy()
    graph_df["fecha"] = graph_df["fecha_hora"].dt.date
    graph_df["hora"] = graph_df["fecha_hora"].dt.hour
    fig1 = px.line(graph_df, x="hora", y="potencia_solar [kW]", color="fecha", markers=True, color_discrete_sequence=color_palette)
    fig1.update_layout(xaxis_title="hora [h]", yaxis_title='potencia solar [kW]', legend={"title": "fecha"})
    st.plotly_chart(fig1, theme="streamlit", use_container_width=True)

    # Second graph: Power values by hour
    st.header("Valores de potencia por hora")
    date_list = list(graph_df['fecha'].unique())
    for date in date_list:
        mini_df = graph_df[graph_df['fecha'] == date]
        fecha = mini_df['fecha_hora'].astype(object).unique()[0].strftime("%Y-%m-%d")
        dia_semana = mini_df['fecha_hora'].astype(object).unique()[0].strftime("%A")
        # Week dict
        week_dict = {
            "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
            "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"
        }
        dia_semana = week_dict[dia_semana]
        fig = px.bar(mini_df, x='hora', y='radiacion_directa [kW/m²]', color='radiacion_directa [kW/m²]')
        st.subheader(f"{fecha}, {dia_semana}")
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)