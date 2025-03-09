from datetime import datetime, timedelta, date
from typing import Optional
import pandas as pd
import numpy as np

def format_fecha(fecha_str: str, _format: str = "%Y-%m-%d") -> str:
    """
    Formatea una fecha en formato ISO a un formato más legible.
    """
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    dt = datetime.strptime(fecha_str, _format)
    return f"{dt.day} {meses[dt.month - 1]} {dt.year}"

def truncate_date_range(earliest, latest, fecha_ini: Optional[str], fecha_fin: Optional[str]):

    if fecha_ini is None and fecha_fin is None:
        fecha_ini = (latest - timedelta(days=365)).isoformat()
        fecha_fin = latest.isoformat()
        return fecha_ini, fecha_fin

    if fecha_ini is None:
        fecha_ini = earliest
    else:
        fecha_ini = date.fromisoformat(fecha_ini)

    if fecha_fin is None:
        fecha_fin = latest
    else:
        fecha_fin = date.fromisoformat(fecha_fin)

    if fecha_ini > fecha_fin:
        temp = fecha_ini
        fecha_ini = fecha_fin
        fecha_fin = temp

    diff = fecha_fin - fecha_ini

    if diff.days > 365:
        fecha_ini = fecha_fin - timedelta(days=365)

    return fecha_ini.isoformat(), fecha_fin.isoformat()

def convert_latitude(lat):
    # Extract degrees and minutes
    degrees = int(lat[:-5])  # First 4 digits are degrees
    minutes = int(lat[-5:-3])  # Last 2 digits are minutes

    # Convert to decimal degrees
    latitude_decimal = degrees + minutes / 60.0
    if lat[-1] == 'S':  # If South, make negative
        latitude_decimal = -latitude_decimal
    return latitude_decimal


def convert_longitude(lon):
    # Extract degrees and minutes
    degrees = int(lon[:-5])  # First 4 digits are degrees
    minutes = int(lon[-5:-3])  # Last 2 digits are minutes

    # Convert to decimal degrees
    longitude_decimal = degrees + minutes / 60.0
    if lon[-1] == 'W':  # If West, make it negative
        longitude_decimal = -longitude_decimal
    return longitude_decimal

def provincia_avg(df):
    """For use in choropleth maps
        This function does the following:
        - Filters the DataFrame to only include the necessary columns for the choropleth map
        - Converts the 'provincia_id' column to string for combining with geojson
        - Converts the rest of the columns to numeric for averaging
        - Adds 'provincia_id' by merging with locations_df
        - Groups by 'provincia_id' and calculates the mean of each column
        - Returns the resulting DataFrame with the mean values for each provincia
    """

    # Load locations_df
    locations_df = pd.read_csv('data/locations.csv')

    # Add provincia_id
    df = df.merge(locations_df[['idema', 'provincia_id', 'provincia']], on='idema', how='left')

    # Filter necessary columns
    cols = ['provincia_id', 'provincia'] + df.select_dtypes(include=['number']).columns.tolist()
    df = df[cols]

    # Convert provincia_id to string
    df['provincia_id'] = df['provincia_id'].astype(str)
    # Convert the rest to numeric
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

    # Return df of provincia means
    return df.groupby('provincia_id').agg({
        'provincia': 'first',  # Retain the first (or last) 'nombre provincia' per group
        **{col: 'mean' for col in df.select_dtypes(include=['number']).columns if col != 'provincia_id'}
    }).reset_index()


def log_transform_df(df, numeric_cols: Optional[list[str]] = None, epsilon=1e-10):

    df_log = df.copy()

    if not numeric_cols:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    if not numeric_cols:
        return df_log

    min_value = df_log[numeric_cols].min().min()

    shift_value = abs(min_value) + epsilon if min_value <= 0 else 0
    df_log[numeric_cols] = df_log[numeric_cols].apply(lambda x: x + shift_value)

    df_log[numeric_cols] = df_log[numeric_cols].apply(np.log)

    df_log = df_log.round(4)

    return df_log
