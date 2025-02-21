import os
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
