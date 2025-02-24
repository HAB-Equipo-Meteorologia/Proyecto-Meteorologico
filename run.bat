:: UNTESTED (I don't have Windows to test this)

@echo off

if not exist logs (
    mkdir logs
)

run_tests.bat

:: Start FastAPI
start "" uvicorn src.api.main:app --reload --host localhost --port 8000 >> logs\fastapi.log 2>&1

:: Start Streamlit
start "" streamlit run streamlit_app.py --server.port 8501 --server.address localhost >> logs\streamlit.log 2>&1

pause
