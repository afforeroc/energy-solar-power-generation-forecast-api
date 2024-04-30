# -*- coding: utf-8 -*-

"""
This module provides utility functions
Author: Andres Felipe Forero Correa
Date: 2023-04-18
"""
import io
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import json
import base64
from datetime import datetime
from tzlocal import get_localzone
import pandas as pd
import streamlit as st


def validate_keys(input_dict, key_list):
    """Validate if all keys are in the dictionary or not"""
    missing_keys = []
    for key in key_list:
        if key not in input_dict:
            missing_keys.append(key)
    return missing_keys


def is_valid_number_str(value_str):
    """Validate if a string is a valid number (integer, float)"""
    try:
        float(value_str)
        return True
    except ValueError:
        return False


def is_valid_date_str(value_str, date_format="%Y-%m-%d"):
    """Validate if a string is a valid datetime"""
    try:
        datetime.strptime(value_str, date_format)
        return True
    except ValueError:
        return False


def st_validate_param_value_is_empty(param_dict, param):
    """Validate if a param value is empty"""
    value = param_dict[param]
    if len(value) == 0:
        st.error(f"ERROR: El valor del parámetro '{param}' en la URL está vacio.", icon="🚨")
        st.stop()


def st_validate_param_value_is_number(param_dict, param):
    """Validate if a param value is a number"""
    value = param_dict[param]
    if not is_valid_number_str(value):
        st.error(f"ERROR: El valor '{value}' del parámetro '{param}' en la URL no representa un número válido.", icon="🚨")
        st.stop()


def st_validate_param_value_is_date(param_dict, param):
    """Validate if a param value is a date"""
    value = param_dict[param]
    if not is_valid_date_str(value):
        st.error(f"ERROR: El valor '{value}' del parámetro '{param}' en la URL no representa una fecha válida.", icon="🚨")
        st.stop()


def st_validate_value_range_of_param_value(param, value, min_value, max_value):
    """Validate if a param value is in value range"""
    if not min_value <= value <= max_value:
        if isinstance(value, datetime):
            st.error(f"ERROR: El valor '{value.strftime('%Y-%m-%d')}' del parámetro '{param}' en la URL no pertenece al rango de valores entre '{min_value.strftime('%Y-%m-%d')}' y '{max_value.strftime('%Y-%m-%d')}'.", icon="🚨")
            st.stop()
        st.error(f"ERROR: El valor '{value}' del parámetro '{param}' en la URL no pertenece al rango de valores entre '{min_value}' y '{max_value}'.", icon="🚨")
        st.stop()


def fetch_json(url):
    """Fetch JSON data from a URL request and handle errors"""
    try:
        with urlopen(url) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except HTTPError as error:
        print(f"HTTP Error {error.code}: {error.reason}")
        return None
    except URLError as error:
        print(f"URL Error: {error.reason}")
        return None
    except Exception as error:
        print(f"Unexpected Error: {error}")
        return None


def get_weather_df_from_open_meteo_json(json_data):
    """Create a weather dataframe extracting json data (from Open Meteo API)"""
    weather_df = pd.DataFrame()
    for param in json_data['hourly_units'].keys():
        param_unit = f"{param} [{json_data['hourly_units'][param]}]"
        weather_df[param_unit] = json_data['hourly'][param]
    param_time = f"time [{json_data['hourly_units']['time']}]"
    weather_df['datetime'] = pd.to_datetime(weather_df[param_time])
    weather_df = weather_df.drop(columns=[param_time])
    return weather_df


def create_csv_download_link(df, filename_base, html_text):
    """Create a download link for a DataFrame in CSV format"""
    csv_data = df.to_csv(index=False).encode()
    b64 = base64.b64encode(csv_data).decode()
    filename = f"{filename_base}.xlsx"
    link = f'<a href="data:application/octet-stream;base64,{b64}" \
        download="{filename}">{html_text}</a>'
    return link


def create_excel_download_link_one_sheet(dataframes, filename_base, html_text, sheet_name="Sheet1"):
    """Create a download link for multiple DataFrames in Excel format on the same sheet"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        startrow = 0
        for df in dataframes:
            df.to_excel(writer, index=False, sheet_name=sheet_name, startrow=startrow)
            startrow += df.shape[0] + 2
    output.seek(0)
    excel_data = output.read()
    b64 = base64.b64encode(excel_data).decode()
    filename = f"{filename_base}.xlsx"
    link = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" \
             download="{filename}">{html_text}</a>'
    return link


def obtain_time_zone_name():
    """Obtain time zone local"""
    local_timezone = get_localzone()
    time_zone_name = local_timezone.key
    return time_zone_name
