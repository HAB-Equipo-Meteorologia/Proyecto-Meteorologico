import os
import json
from dotenv import load_dotenv, find_dotenv

if bool(find_dotenv()):
    load_dotenv()
    DEV_MODE = os.getenv('DEV') == 'true'
else:
    DEV_MODE = False

try:
    import streamlit as st

    STREAMLIT_MODE = 'secrets' in st.__dict__ and bool(st.secrets)
except (FileNotFoundError, ImportError):
    STREAMLIT_MODE = False


def get_env_var(key: str) -> str:
    """Retrieve environment variable from .env (dev) or Streamlit secrets (prod)."""

    if STREAMLIT_MODE:
        try:
            value = st.secrets[key]
        except KeyError:
            raise ValueError(f"Error: {key} not found in Streamlit secrets")

    else:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Error: {key} not found in .env file")

    return value


api_host = get_env_var("API_HOST")
streamlit_host = get_env_var("STREAMLIT_HOST")

if DEV_MODE:
    api_port = get_env_var("API_PORT")
    streamlit_port = get_env_var("STREAMLIT_PORT")
    api_url = f"http://{api_host}:{api_port}/api"
    streamlit_url = f"http://{streamlit_host}:{streamlit_port}"
else:
    api_url = f"https://{api_host}/api"
    streamlit_url = f"https://{streamlit_host}"

with open('data/locations/comunidades.json') as f:
    comunidades = json.load(f)

with open('data/locations/provincias.json') as f:
    provincias = json.load(f)

with open('data/locations/municipios.json') as f:
    municipios = json.load(f)

with open('data/locations/estaciones.json') as f:
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

