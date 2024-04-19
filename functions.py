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
# from datetime import datetime
import pandas as pd


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


def create_csv_download_link(df, filename, html_text):
    """Create a download link for a DataFrame in CSV format"""
    csv_data = df.to_csv(index=False).encode()
    b64 = base64.b64encode(csv_data).decode()
    link = f'<a href="data:application/octet-stream;base64,{b64}" \
        download="{filename}">{html_text}</a>'
    return link


def create_excel_download_link(df, filename, html_text):
    """Create a download link for a DataFrame in Excel format"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    excel_data = output.read()
    b64 = base64.b64encode(excel_data).decode()
    link = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" \
             download="{filename}">{html_text}</a>'
    return link

#def is_valid_number_str(value_str):
#    if value_str.isdigit():
#        return True
#    try:
#        _ = float(value_str)
#        return True
#    except ValueError:
#        return False

#def is_valid_date_str(date_str):
#    try:
#        datetime.strptime(date_str, '%Y-%m-%d')
#        return True
#    except ValueError:
#        return False
