#!/bin/bash

mkdir -p logs

./run_tests.sh

# Start FastAPI
uvicorn src.api.main:app --reload --host localhost --port 8000 2>&1 | tee logs/fastapi.log &

# Start Streamlit
streamlit run streamlit_app.py --server.port 8501 --server.address localhost 2>&1 | tee logs/streamlit.log &

wait
