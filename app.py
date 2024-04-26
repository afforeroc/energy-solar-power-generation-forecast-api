# -*- coding: utf-8 -*-
# URL sample: http://localhost:8501/?code=NX3756329Z&capacity=456&voltage=789&latitude=6.248&longitude=-75.57&area=314.16&start_date=2024-04-25&end_date=2024-05-01
"""
Title: ECS: Predicción de energía solar
Description: Web app that predicts solar power using OpenMeteo API.
Author: Andres Felipe Forero Correa
Date: 2024-04-18
"""

from datetime import datetime, timedelta
import plotly.express as px
import streamlit as st
from functions import validate_keys, st_validate_param_value_is_empty, st_validate_param_value_is_number, st_validate_param_value_is_date, st_validate_value_range_of_param_value, \
    fetch_json, get_weather_df_from_open_meteo_json, create_excel_download_link, get_server_time_zone, get_client_time_zone, calculate_time_zone_difference

# Constants
forecast_days = 7
delta_days = forecast_days - 1
mega = 10e6
kilo = 10e3
param_names = ["latitude", "longitude", "area", "start_date", "end_date", "code", "capacity", "voltage"]
main_weather_variable_en = "direct_radiation"
main_weather_variable_es = "radiacion_directa"
week_en_es_dict = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
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
    min_date = datetime.combine(datetime.now().date(), datetime.min.time())
    max_date = min_date + timedelta(days=delta_days)
    # Convert URL params in a dict and validate all params
    param_dict = st.query_params.to_dict()
    missing_params = validate_keys(param_dict, param_names)
    # Validate each param and extract its value
    if len(missing_params) == 0:
        # Validate if a param value is empty
        for param in param_dict:
            st_validate_param_value_is_empty(param_dict, param)
        # Validate data types
        st_validate_param_value_is_number(param_dict, "capacity")
        st_validate_param_value_is_number(param_dict, "voltage")
        st_validate_param_value_is_number(param_dict, "latitude")
        st_validate_param_value_is_number(param_dict, "longitude")
        st_validate_param_value_is_number(param_dict, "area")
        st_validate_param_value_is_date(param_dict, "start_date")
        st_validate_param_value_is_date(param_dict, "end_date")
        # Extract the param values and convert them in best data type
        code = param_dict["code"]
        capacity = float(param_dict["capacity"])
        voltage = float(param_dict["voltage"])
        latitude = float(param_dict["latitude"])
        longitude = float(param_dict["longitude"])
        area = float(param_dict["area"])
        start_date = datetime.strptime(param_dict["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(param_dict["end_date"], "%Y-%m-%d")
        # Validate range value of each param value
        st_validate_value_range_of_param_value("latitude", latitude, -90, 90)
        st_validate_value_range_of_param_value("longitude", longitude, -180, 180)
        st_validate_value_range_of_param_value("area", area, 0.0001, float('inf'))
        st_validate_value_range_of_param_value("start_date", start_date, min_date, max_date)
        st_validate_value_range_of_param_value("end_date", end_date, min_date, max_date)
        # Show codigo, capacidad and tension
        st.markdown(f"Código: **{code}**")
        st.markdown(f"Capacidad nominal [kVA]: **{capacity}**")
        st.markdown(f"Tensión nominal [kV]: **{voltage}**")
        # Interpolate input data using forms
        latitude = st.number_input("Latitud", value=latitude, min_value=-90.0, max_value=90.0)
        longitude = st.number_input("Longitud", value=longitude, min_value=-180.0, max_value=180.0)
        area = st.number_input("Área [m²]", value=area, min_value=0.0001)
        start_date = st.date_input("Fecha inicial", value=start_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("Fecha final", value=end_date, min_value=min_date, max_value=max_date)
    elif len(missing_params) == len(param_names):
        bogota_dict = {"latitude": 4.62, "longitude": -74.06, "area": 161.80}
        latitude = st.number_input("Latitud", value=bogota_dict["latitude"], min_value=-90.0, max_value=90.0)
        longitude = st.number_input("Longitud", value=bogota_dict["longitude"], min_value=-180.0, max_value=180.0)
        area = st.number_input("Área [m²]", value=bogota_dict["area"], min_value=0.0001)
        start_date = st.date_input("Fecha inicial", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("Fecha final", value=max_date, min_value=min_date, max_value=max_date)
    else:
        missing_params_str = ", ".join(f"'{param}'" for param in missing_params)
        st.error(f"ERROR: Faltan los siguientes parámetros en la URL: {missing_params_str}", icon="🚨")
        st.stop()
    # Push button
    if st.button("Predecir"):
        # Validate ranges of values for each variable
        if not end_date >= start_date:
            st.error("ERROR: La 'Fecha inicial' debe ser menor o igual que la 'Fecha final'.", icon="🚨")
            st.stop()
        # Format the OPEN_METEO_URL_TEMPLATE
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        open_meteo_api_url = OPEN_METEO_API_URL_TEMPLATE.format(latitude=latitude, longitude=longitude,
                                                                start_date=start_date_str, end_date=end_date_str,
                                                                weather_variables_str=main_weather_variable_en)
        # Test API URL
        # st.header("Test Open Meteo API URL")
        # st.success(open_meteo_api_url)
        # Fetch JSON data
        json_data = fetch_json(open_meteo_api_url)
        # Forecast dataframe from JSON data
        forecast_df = get_weather_df_from_open_meteo_json(json_data)
        forecast_df = forecast_df.rename(columns={"datetime": "fecha_hora"})
        forecast_df = forecast_df.set_index("fecha_hora")
        # Replace negative values by zero
        forecast_df.loc[forecast_df[f"{main_weather_variable_en} [W/m²]"] < 0, f"{main_weather_variable_en} [W/m²]"] = 0
        # Convert weather variable columns from Watts to kilo Watts
        forecast_df[f"{main_weather_variable_es} [kW/m²]"] = forecast_df[f"{main_weather_variable_en} [W/m²]"] / kilo
        # Delete old column
        forecast_df = forecast_df.drop(columns=[f"{main_weather_variable_en} [W/m²]"])
        # Obtain solar power generation from main weather variable
        forecast_df["potencia_solar [kW]"] = forecast_df[f"{main_weather_variable_es} [kW/m²]"] * area
        # Round decimals
        forecast_df["radiacion_directa [kW/m²]"] = forecast_df["radiacion_directa [kW/m²]"].round(3)
        forecast_df["potencia_solar [kW]"] = forecast_df["potencia_solar [kW]"].round(3)
        # Show output dataframe
        st.header("Dataframe de predicción")
        st.dataframe(forecast_df)
        # Download in excel
        output_filename = f"prediccion_solar_lat_{latitude}_lon_{longitude}_area_{area}_{start_date_str}_{end_date}"
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
        # Plot 1
        fig1 = px.area(graph_df, x="fecha_hora", y="potencia_solar [kW]",
                       labels={"fecha_hora": "Fecha-hora", "potencia_solar [kW]": "Potencia a generar [kW]"},
                       color_discrete_sequence=color_palette2)
        st.header("Curvas de potencia total")
        fig1.update_layout(xaxis={"showgrid": True, "gridwidth": 1, "gridcolor": 'lightgray'},
                           yaxis={"showgrid": True, "gridwidth": 1, "gridcolor": 'lightgray'})
        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
        # Plot 2
        fig2 = px.line(graph_df, x="hora", y="potencia_solar [kW]", color="fecha",
                       labels={"hora": "Hora [h]", "potencia_solar [kW]": "Potencia a generar [kW]", "fecha": "Fecha"},
                       markers=True, color_discrete_sequence=color_palette1)
        fig2.update_layout(xaxis={"showgrid": True, "gridwidth": 1, "gridcolor": 'lightgray'},
                           yaxis={"showgrid": True, "gridwidth": 1, "gridcolor": 'lightgray'})
        st.header("Curvas de potencia diarias")
        st.plotly_chart(fig2, theme="streamlit", use_container_width=True)
        # Plot 3
        st.header("Potencia por hora en el día")
        for idx, date in enumerate(date_list):
            # Extract mini df
            mini_df = graph_df[graph_df["fecha"] == date]
            # Set week day in spanish
            week_day_en = mini_df["fecha_hora"].astype(object).unique()[0].strftime("%A")
            week_day_es = week_en_es_dict[week_day_en]
            # Set color scale related with first section
            color_for_date = color_palette1[idx % len(color_palette1)]
            custom_colorscale = [[0.0, "#FFFFFF"], [1.0, color_for_date]]
            # Plot for each date
            fig_aux = px.bar(mini_df, x="hora", y="potencia_solar [kW]",
                             labels={"hora": "Hora [h]", "potencia_solar [kW]": "Potencia a generar [kW]"},
                             color="potencia_solar [kW]", color_continuous_scale=custom_colorscale)
            fig_aux.update_layout(xaxis={"showgrid": True, "gridwidth": 1, "gridcolor": 'lightgray'},
                                  yaxis={"showgrid": True, "gridwidth": 1, "gridcolor": 'lightgray'})
            st.subheader(f"{week_day_es}, {(date.day)} de {month_dict[date.month]} de {date.year}")
            st.plotly_chart(fig_aux, theme="streamlit", use_container_width=True)

        # Get and display the time zones
        server_time_zone = get_server_time_zone()
        client_time_zone = get_client_time_zone()

        st.markdown(f"Server Time Zone: **{server_time_zone}**")
        st.markdown(f"Client Time Zone: **{client_time_zone}**")

        # Calculate and display the time zone difference
        time_zone_difference = calculate_time_zone_difference()
        st.markdown(f"Time Zone Difference between Server and Client: **{time_zone_difference}**")