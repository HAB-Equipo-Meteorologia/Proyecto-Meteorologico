import streamlit as st

st.set_page_config(page_title="Análisis Meteorológico", page_icon=":lightning:", layout="wide",
                   initial_sidebar_state="expanded")


def main():
    pages = {
        "Principal": [
            st.Page("src/streamlit_app/Pages/Main/Dashboard.py", title="Welcome"),
            st.Page("src/streamlit_app/Pages/Main/API Docs.py", title="API Docs")
        ],
        "Histórico": [
            st.Page("src/streamlit_app/Pages/Historical/Estacion.py", title="Estación"),
        ],
    }

    pg = st.navigation(pages)
    pg.run()
