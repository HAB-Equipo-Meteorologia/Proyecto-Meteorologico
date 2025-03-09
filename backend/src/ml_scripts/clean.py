import sys
sys.path.append('../../..')
from helpers import lookups
import pandas as pd
import numpy as np


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    
    df_clean = df.copy()

    df_clean['fecha'] = pd.to_datetime(df_clean['fecha'])
    df_clean['year'] = df_clean['fecha'].dt.year

    df_clean = df_clean.merge(lookups.locations_df[['idema', 'latitud', 'altitud']], on='idema', how='left')
    df_clean['fecha_day'] = df_clean['fecha'].dt.dayofyear
    
    df_clean['fecha_sin'] = df_clean.apply(
        lambda row: (np.sin(2 * np.pi * row['fecha_day'] / 366) + 1) / 2 if row['year'] % 4 == 0 
        else (np.sin(2 * np.pi * row['fecha_day'] / 365) + 1) / 2, axis=1)
    
    df_clean['fecha_cos'] = df_clean.apply(
        lambda row: (np.cos(2 * np.pi * row['fecha_day'] / 366) + 1) / 2 if row['year'] % 4 == 0 
        else (np.cos(2 * np.pi * row['fecha_day'] / 365) + 1) / 2, axis=1)

    numeric_cols = df_clean.drop(columns=['fecha', 'idema']).columns
    df_clean[numeric_cols] = df_clean[numeric_cols].apply(pd.to_numeric, errors='coerce')

    df_clean = df_clean.drop(columns=['fecha_day', 'year'])

    df_clean = df_clean.round(4)

    return df_clean
