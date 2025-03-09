#!/bin/bash

mkdir -p logs

echo "Starting FastAPI..."

# Set up paths
PYTHONPATH=$PYTHONPATH:$(pwd)
export PYTHONPATH

# Start FastAPI with its own .env file
cd backend || exit
uvicorn src.main:app --reload --host localhost --port 8000 2>&1 | tee ../logs/fastapi.log & disown
cd ..

echo "Starting Streamlit..."

# Start Streamlit with its own .env file
cd frontend || exit
streamlit run src/streamlit_app.py --server.port 8501 --server.address localhost 2>&1 | tee ../logs/streamlit.log & disown
cd ..

wait
