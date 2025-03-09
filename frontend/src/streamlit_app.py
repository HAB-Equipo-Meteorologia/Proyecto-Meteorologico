import streamlit as st
from frontend.src.services.background import check_latest
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Análisis Meteorológico", page_icon=":lightning:", layout="wide",
                   initial_sidebar_state="expanded")

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def main():
    pages = {
        "Principal": [
            st.Page("Pages/Main/Dashboard.py", title="👋 Bienvenidos"),
            st.Page("Pages/Main/About_us.py", title="👩‍💻 Sobre nosotras"),
        ],
        "Análisis Exploratorio de Datos": [
            st.Page("Pages/EDA/Graficos.py", title="📈 Gráficos"),
            st.Page("Pages/EDA/Mapa.py", title="🗺️ Mapa"),
        ],
        "Machine Learning": [
            st.Page("Pages/ML/ML-Intro.py", title="🤖 Introducción"),
            st.Page("Pages/ML/ML-Modelos.py", title="🧠 Modelos"),
        ],
        "Datos": [
            st.Page("Pages/Datasets/Datasets-Historico.py", title="📚 Datos Históricos"),
            st.Page("Pages/Datasets/Datasets-ML.py", title="📊 Datos ML"),
        ],
        "API": [
            st.Page("Pages/API/API Docs.py", title="📜 API Docs")
        ]
    }

    check_latest()

    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()