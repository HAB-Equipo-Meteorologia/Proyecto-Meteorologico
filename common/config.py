import os
from dotenv import load_dotenv, find_dotenv
from common.logger import setup_logger

logger = setup_logger('config')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

if bool(find_dotenv()):
    load_dotenv()
    DEV_MODE = os.getenv('DEV') == 'true'
else:
    DEV_MODE = False

logger.debug(f"DEV MODE: {DEV_MODE}")

api_host = os.environ["API_HOST"]
streamlit_host = os.environ["STREAMLIT_HOST"]

if DEV_MODE:
    api_port = os.environ["API_PORT"]
    streamlit_port = os.environ["STREAMLIT_PORT"]
    api_url = f"http://{api_host}:{api_port}/api"
    streamlit_url = f"http://{streamlit_host}:{streamlit_port}"
else:
    api_url = f"https://{api_host}/api"
    streamlit_url = f"https://{streamlit_host}"

logger.debug(f"API URL: {api_url}")
logger.debug(f"Streamlit URL: {streamlit_url}")
