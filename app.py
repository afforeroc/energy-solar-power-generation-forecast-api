# -*- coding: utf-8 -*-

"""
Predicción de energía solar: web app that
predicts solar power using OpenMeteo API.
Author: Andres Felipe Forero Correa
Date: 2024-04-18
"""

from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import plotly.express as px
import streamlit as st
from modules.functions import fetch_json, get_weather_df_from_open_meteo_json, create_excel_download_link


# Functions
def obtain_timezone(lat_in, lon_in):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=lat_in, lng=lon_in)
    return timezone_str


# Constants
forecast_days = 7
min_date = datetime.today() + timedelta(days=1)
max_date = min_date + timedelta(days=forecast_days-1)
mega = 10e6
kilo = 10e3
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
# weather_variables = ["direct_radiation", "direct_radiation_instant", "direct_normal_irradiance", "direct_normal_irradiance_instant"]
# weather_variables_str = (",").join(weather_variables)
OPEN_METEO_API_URL_TEMPLATE = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly={weather_variables_str}&timezone={timezone}"


if __name__ == "__main__":
    # URL template: http://localhost:8501/?latitude=4.14924&longitude=-74.88429&area=100&start_date=2024-04-17&end_date=2024-04-24
    # Page title, title and caption of the web app
    st.set_page_config(page_title="DERMS: Predicción de energía solar", page_icon="🌞")
    st.title("Predicción de Energía Solar")
    st.caption("Sistema de predicción de generación de energía solar de Energy Computer Systems")
    # Obtain today and seven days forwarth dates
    current_date = datetime.now().date()
    six_days_forwarth_date = current_date + timedelta(days=forecast_days-1)
    # Dates in str
    today_date_str = current_date.strftime("%Y-%m-%d")
    seven_days_forwarth_date_str = six_days_forwarth_date.strftime("%Y-%m-%d")
    # Extract params from URL
    params = st.query_params
    latitude = params.get("latitude", "0")
    longitude = params.get("longitude", "0")
    area = params.get("area", "100")
    start_date = params.get("start_date", today_date_str)
    end_date = params.get("end_date", seven_days_forwarth_date_str)
    # Show extracted data from URL or the default values
    latitude = st.text_input("Latitud", latitude)
    longitude = st.text_input("Longitud", longitude)
    area = st.text_input("Área", area)
    start_date = st.date_input("Fecha inicial", value=datetime.strptime(start_date, "%Y-%m-%d"))
    end_date = st.date_input("Fecha final", value=datetime.strptime(end_date, "%Y-%m-%d"))
    timezone = obtain_timezone(float(latitude), float(longitude))
    # Format the OPEN_METEO_URL_TEMPLATE
    open_meteo_api_url = OPEN_METEO_API_URL_TEMPLATE.format(latitude=latitude, longitude=longitude, area=area, start_date=start_date, end_date=end_date, weather_variables_str=main_weather_variable_en, timezone=timezone)
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
    # Show output dataframe
    st.header("Dataframe de predicción")
    st.dataframe(forecast_df)
    # Download in excel
    output_filename = f"prediccion_solar_lat{latitude}_lon{longitude}_area{area}"
    excel_filename = output_filename + ".xlsx"
    download_excel_link = create_excel_download_link(forecast_df.reset_index(), excel_filename, "Descargar Excel")
    st.markdown(download_excel_link, unsafe_allow_html=True)
    # Create graph_df and color_palette
    graph_df = forecast_df.reset_index().copy()
    graph_df["fecha"] = graph_df["fecha_hora"].dt.date
    graph_df["hora"] = graph_df["fecha_hora"].dt.hour
    date_list = list(graph_df["fecha"].unique())
    color_palette = px.colors.qualitative.Plotly[:len(date_list)]
    # First section for plots
    fig1 = px.line(graph_df, x="hora", y="potencia_solar [kW]", color="fecha",
                   labels={"hora": "Hora [h]", "potencia_solar [kW]": "Potencia solar [kW]"},
                   markers=True, color_discrete_sequence=color_palette)
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
        color_for_date = color_palette[idx % len(color_palette)]
        custom_colorscale = [[0.0, "#FFFFFF"], [1.0, color_for_date]]
        # Plot for each date
        fig_aux = px.bar(mini_df, x="hora", y="potencia_solar [kW]",
                         labels={"hora": "Hora [h]", "potencia_solar [kW]": "Potencia solar [kW]"},
                         color="potencia_solar [kW]",
                         color_continuous_scale=custom_colorscale)
        st.subheader(f"{week_day_es.capitalize()}, {(date.day)} de {month_dict[date.month]} de {date.year}")
        st.plotly_chart(fig_aux, theme="streamlit", use_container_width=True)
