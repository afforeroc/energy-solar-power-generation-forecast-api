# -*- coding: utf-8 -*-
# URL sample: http://localhost:8501/?latitude=89.00&longitude=-74.88&area=100&start_date=2024-04-17&end_date=2024-04-23
"""
Title: ECS: Predicción de energía solar
Description: Web app that predicts solar power using OpenMeteo API.
Author: Andres Felipe Forero Correa
Date: 2024-04-18
"""

import random
from datetime import datetime, timedelta
import plotly.express as px
import streamlit as st
from lorem_text import lorem
import string
from functions import fetch_json, get_weather_df_from_open_meteo_json, create_excel_download_link

# Constants
forecast_days = 7
delta_days = forecast_days - 1
mega = 10e6
kilo = 10e3
tension_values = [0.22, 13.2, 13.8, 34.5]
main_weather_variable_en = "direct_radiation"
main_weather_variable_es = "radiacion_directa"
week_dict = {
    "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
    "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"
}
month_dict = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}
OPEN_METEO_API_URL_TEMPLATE = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly={weather_variables_str}&timezone=auto"


if __name__ == "__main__":
    # Page title, title and caption of the web app
    st.set_page_config(page_title="ECS: Predicción energía solar", page_icon="🌞")
    st.title("Predicción de energía solar")
    st.caption("Sistema de predicción de generación de energía solar de Energy Computer Systems")
    # Obtain today and seven days forwarth dates
    today_date = datetime.now().date()
    today_plus_delta_date = today_date + timedelta(days=delta_days)
    # Dates in str
    today_date_str = today_date.strftime("%Y-%m-%d")
    today_plus_delta_date_str = today_plus_delta_date.strftime("%Y-%m-%d")
    # Extract params from URL
    params = st.query_params
    if len(params) == 0:
        caracteres = string.ascii_letters + string.digits
        codigo_str = ''.join(random.choices(caracteres, k=10)).upper()
        descripcion_str = lorem.words(20)
        capacidad_str = str(round(random.uniform(2, 100), 3))
        random.shuffle(tension_values)
        tension_str =  str(round(tension_values[0], 3))
        latitude_str = "4.624335"
        longitude_str = "-74.063644"
        area_str = str(round(random.uniform(7, 745), 3))
        start_date_str = today_date_str
        end_date_str = today_plus_delta_date_str
    elif len(params) == 9:
        codigo_str = params.get("codigo")
        descripcion_str = params.get("descripcion")
        capacidad_str = params.get("capacidad")
        tension_str = params.get("tension")
        latitude_str = params.get("latitude")
        longitude_str = params.get("longitude")
        area_str = params.get("area")
        start_date_str = params.get("start_date")
        end_date_str = params.get("end_date")
    # Show basic information
    st.markdown(f"Código: ***{codigo_str}***")
    st.markdown(f"Descripción: ***{descripcion_str}***")
    st.markdown(f"Capacidad nominal [kVA]: ***{capacidad_str}***")
    st.markdown(f"Tensión [kV]: ***{tension_str}***")
    # Interpolate input data using forms
    latitude = st.number_input("Latitud", value=float(latitude_str))
    longitude = st.number_input("Longitud", value=float(longitude_str))
    area = st.number_input("Área [m²]", value=float(area_str))
    start_date = st.date_input("Fecha inicial", min_value=today_date, max_value=today_plus_delta_date, value=datetime.strptime(start_date_str, "%Y-%m-%d"))
    end_date = st.date_input("Fecha final", min_value=today_date, max_value=today_plus_delta_date, value=datetime.strptime(end_date_str, "%Y-%m-%d"))
    # Push the botton
    if st.button('Predecir') or len(params) > 0:
        # Validate ranges of values for each variable
        if not -90 < latitude < 90:
            st.error("ERROR: El valor de la 'Latitud' debe estar entre -90 y 90.", icon="🚨")
            st.stop()
        if not -180 < longitude < 180:
            st.error("ERROR: El valor de la 'Latitud' debe estar entre -180 y 180.", icon="🚨")
            st.stop()
        if not area > 0:
            st.error("ERROR: El valor de la 'Área' debe ser mayor que cero.", icon="🚨")
            st.stop()
        if not end_date >= start_date:
            st.error("ERROR: La 'Fecha inicial' debe ser menor o igual que la 'Fecha final'.", icon="🚨")
            st.stop()

        # Format the OPEN_METEO_URL_TEMPLATE
        open_meteo_api_url = OPEN_METEO_API_URL_TEMPLATE.format(latitude=latitude, longitude=longitude, area=area, start_date=start_date, end_date=end_date, weather_variables_str=main_weather_variable_en)
        # Test API URL
        # st.header("Test Open Meteo API URL")
        # st.success(open_meteo_api_url)
        # Fetch JSON data
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
        forecast_df["potencia_solar [kW]"] = forecast_df[f"{main_weather_variable_es} [kW/m²]"] * float(area)
        # Round decimals
        forecast_df["radiacion_directa [kW/m²]"] = forecast_df["radiacion_directa [kW/m²]"].round(3)
        forecast_df["potencia_solar [kW]"] = forecast_df["potencia_solar [kW]"].round(3)
        # Show output dataframe
        st.header("Dataframe de predicción")
        st.dataframe(forecast_df)
        # Download in excel
        output_filename = f"prediccion_solar_lat{latitude}_lon{longitude}_area{area}"
        excel_filename = output_filename + ".xlsx"
        download_excel_link = create_excel_download_link(forecast_df.reset_index(), excel_filename, "Descargar Excel")
        st.markdown(download_excel_link, unsafe_allow_html=True)
        # Create graph_df
        graph_df = forecast_df.reset_index().copy()
        graph_df["fecha"] = graph_df["fecha_hora"].dt.date
        graph_df["hora"] = graph_df["fecha_hora"].dt.hour
        date_list = list(graph_df["fecha"].unique())
        # Palette of colors for plots
        color_palette1 = px.colors.qualitative.Plotly[:len(date_list)]
        color_palette2 = px.colors.qualitative.D3[:len(date_list)]
        # Zero plot
        fig0 = px.line(graph_df, x="fecha_hora", y="potencia_solar [kW]",
                       labels={"fecha_hora": "Fecha hora", "potencia_solar [kW]": "Potencia a generar [kW]"},
                       markers=True, color_discrete_sequence=color_palette2)
        st.header("Curvas de potencia total")
        fig0.update_layout(xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'), yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'))
        st.plotly_chart(fig0, theme="streamlit", use_container_width=True)
        # First section for plots
        fig1 = px.line(graph_df, x="hora", y="potencia_solar [kW]", color="fecha",
                       labels={"hora": "Hora [h]", "potencia_solar [kW]": "Potencia a generar [kW]", "fecha": "Fecha"},
                       markers=True, color_discrete_sequence=color_palette1)
        fig1.update_layout(xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'), yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'))
        st.header("Curvas de potencia diarias")
        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
        # Second section for plots
        st.header("Potencia por hora en el día")
        for idx, date in enumerate(date_list):
            # Extract mini df
            mini_df = graph_df[graph_df["fecha"] == date]
            # Set week day in spanish
            week_day_en = mini_df["fecha_hora"].astype(object).unique()[0].strftime("%A")
            week_day_es = week_dict[week_day_en]
            # Set color scale related with first section
            color_for_date = color_palette1[idx % len(color_palette1)]
            custom_colorscale = [[0.0, "#FFFFFF"], [1.0, color_for_date]]
            # Plot for each date
            fig_aux = px.bar(mini_df, x="hora", y="potencia_solar [kW]",
                             labels={"hora": "Hora [h]", "potencia_solar [kW]": "Potencia a generar [kW]"},
                             color="potencia_solar [kW]", color_continuous_scale=custom_colorscale)
            fig_aux.update_layout(xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'), yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'))
            st.subheader(f"{week_day_es.capitalize()}, {(date.day)} de {month_dict[date.month]} de {date.year}")
            st.plotly_chart(fig_aux, theme="streamlit", use_container_width=True)
