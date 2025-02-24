import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.config import get_env_var


def test_get_env_var():
    env_vars = ['DEV',
                'DB_USER', 'DB_PASSWORD',
                'DB_HOST', 'DB_PORT', 'DB_NAME',
                'API_HOST', 'API_PORT',
                'STREAMLIT_HOST', 'STREAMLIT_PORT']

    assert os.path.exists('.env'), "Error: .env file not found"

    for var in env_vars:
        assert get_env_var(var) is not None, f"Error: {var} not found in .env file"
