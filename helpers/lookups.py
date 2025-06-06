import json
import pandas as pd
import os
from helpers.config import script_dir

with open(os.path.join(script_dir, '../data/locations/comunidades.json'), encoding='utf-8') as f:
    comunidades = json.load(f)

with open(os.path.join(script_dir, '../data/locations/provincias.json'), encoding='utf-8') as f:
    provincias = json.load(f)

with open(os.path.join(script_dir, '../data/locations/municipios.json'), encoding='utf-8') as f:
    municipios = json.load(f)

with open(os.path.join(script_dir, '../data/locations/estaciones.json'), encoding='utf-8') as f:
    estaciones = json.load(f)

com_ids = comunidades.keys()
com_names = [comunidad['nombre'] for comunidad in comunidades.values()]
comunidad_lookup = {v["nombre"]: k for k, v in comunidades.items()}

prov_ids = provincias.keys()
prov_names = [provincia['nombre'] for provincia in provincias.values()]
provincia_lookup = {v["nombre"]: k for k, v in provincias.items()}

mun_ids = municipios.keys()
mun_names = [municipio['nombre'] for municipio in municipios.values()]
municipio_lookup = {v["nombre"]: k for k, v in municipios.items()}

est_ids = estaciones.keys()
est_names = [estacion['nombre'] for estacion in estaciones.values()]
estacion_lookup = {v["nombre"]: k for k, v in estaciones.items()}

estaciones_df = pd.DataFrame(estaciones).T.assign(idema=lambda x: x.index).reset_index(drop=True)
provincias_df = pd.DataFrame(provincias).T.assign(provincia_id=lambda x: x.index).reset_index(drop=True)
comunidades_df = pd.DataFrame(comunidades).T.assign(com_auto_id=lambda x: x.index).reset_index(drop=True)

provincias_df.rename(columns={'nombre': 'provincia'}, inplace=True)
comunidades_df.rename(columns={'nombre': 'comunidad'}, inplace=True)

estaciones_df['provincia_id'] = estaciones_df['provincia_id'].astype(str)
provincias_df['provincia_id'] = provincias_df['provincia_id'].astype(str)
provincias_df['com_auto_id'] = provincias_df['com_auto_id'].astype(str)
comunidades_df['com_auto_id'] = comunidades_df['com_auto_id'].astype(str)

locations_df = estaciones_df.merge(provincias_df, on='provincia_id', how='left')
locations_df = locations_df.merge(comunidades_df, on='com_auto_id', how='left')

elements = ['temperatura', 'lluvia', 'viento', 'humedad', 'presion', 'sol']
element_cols = ['tmed', 'tmin', 'tmax', 'hora_tmax', 'hora_tmin',
                'prec', 'sol',
                'velmedia', 'racha', 'hora_racha', 'dir',
                'hr_media', 'hr_min', 'hr_max', 'hora_hr_max', 'hora_hr_min',
                'pres_max', 'pres_min']

int_cols = ['hr_media', 'hr_min', 'hr_max']
float_cols = ['tmed', 'tmin', 'tmax', 'prec', 'velmedia', 'racha', 'pres_max', 'pres_min', 'sol']
numeric_cols = int_cols + float_cols
time_cols = ['hora_tmin', 'hora_tmax', 'hora_racha', 'hora_hr_max', 'hora_hr_min']

element_cols_map_numeric = {
    'temperatura': ['tmed', 'tmax', 'tmin'],
    'lluvia': ['prec'],
    'viento': ['velmedia', 'racha'],
    'humedad': ['hr_media', 'hr_min', 'hr_max'],
    'presion': ['pres_max', 'pres_min'],
    'sol': ['sol']
}

element_cols_map = {
    'temperatura': ['tmed', 'tmax', 'tmin', 'hora_tmax', 'hora_tmin'],
    'lluvia': ['prec'],
    'viento': ['velmedia', 'racha', 'hora_racha', 'dir'],
    'humedad': ['hr_media', 'hr_min', 'hr_max', 'hora_hr_max', 'hora_hr_min'],
    'presion': ['pres_max', 'pres_min'],
    'sol': ['sol']
}

element_cols_map_time = {
    'temperatura': ['hora_tmax', 'hora_tmin'],
    'viento': ['hora_racha'],
    'humedad': ['hora_hr_max', 'hora_hr_min']
}

label_maps = {
    'tmed': "Temperatura Media (°C)",
    'tmin': "Temperatura Mínima (°C)",
    'tmax': "Temperatura Máxima (°C)",
    'prec': "Precipitación (mm)",
    'velmedia': "Velocidad Viento (km/h)",
    'racha': "Racha Viento (km/h)",
    'hr_media': "Humedad Relativa Media (%)",
    'hr_min': "Humedad Mínima (%)",
    'hr_max': "Humedad Máxima (%)",
    'pres_max': "Presión Máxima (hPa)",
    'pres_min': "Presión Mínima (hPa)",
    'sol': "Horas de Sol",
    'hora_tmax': "Hora Temperatura Máxima",
    'hora_tmin': "Hora Temperatura Mínima",
    'hora_racha': "Hora Racha Viento",
    'hora_hr_max': "Hora Humedad Máxima",
    'hora_hr_min': "Hora Humedad Mínima"
}

choropleth_color_maps = {
    'tmed': "Oranges",
    'tmin': "OrRd",
    'tmax': "Reds",
    'prec': "Blues",
    'velmedia': "BuGn",
    'racha': "BuGn",
    'hr_media': "YlGnBu",
    'hr_min': "Blues",
    'hr_max': "PuBu",
    'pres_max': "BuPu",
    'pres_min': "Purples",
    'sol': "YlOrRd"
}

histogram_color_maps = {
    'tmed': "Orange",
    'tmin': "Yellow",
    'tmax': "Red",
    'prec': "LightBlue",
    'velmedia': "LightGreen",
    'racha': "Green",
    'hr_media': "Cyan",
    'hr_min': "LightBlue",
    'hr_max': "Blue",
    'pres_max': "Purple",
    'pres_min': "Pink",
    'sol': "Yellow"
}

scatter_color_maps = {
    'temperatura': 'Orange',
    'lluvia': 'LightBlue',
    'viento': 'LightGreen',
    'humedad': 'Cyan',
    'presion': 'Pink',
    'sol': 'Yellow'
}

offset_map = {
    'Semana': 7,
    'Mes': 30,
    '3 Meses': 90,
    '6 Meses': 180,
    '1 Año': 365,
    '2 Años': 730,
    '5 Años': 1825
}