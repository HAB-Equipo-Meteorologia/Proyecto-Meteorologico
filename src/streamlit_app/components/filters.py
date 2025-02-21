import pandas as pd
import streamlit as st
from helpers.lookups import com_names, comunidad_lookup, provincias, provincia_lookup, estacion_lookup, \
    estaciones


def estacion_filter():
    comunidad = st.selectbox("Selecciona la comunidad autónoma", com_names)
    com_id = comunidad_lookup[comunidad]
    st.session_state.com_id = com_id

    prov_names = [provincias[index]["nombre"] for index in provincias if
                  str(provincias[index]["com_auto_id"]) == com_id]
    provincia = st.selectbox("Selecciona la provincia", prov_names)
    prov_id = provincia_lookup[provincia]
    st.session_state.prov_id = prov_id

    est_names = [estaciones[index]["nombre"] for index in estaciones if
                 str(estaciones[index]["provincia_id"]) == prov_id]
    estacion = st.selectbox("Selecciona la estación meteorológica", est_names)
    idema = estacion_lookup[estacion]
    st.session_state.idema = idema

    return com_id, prov_id, idema


def date_range_filter():
    last_week = pd.Timestamp.now() - pd.DateOffset(weeks=2)

    _, ini, _, fin, _ = st.columns([2, 5, 2, 5, 2])

    with ini:
        fecha_ini = str(
            st.date_input(label="Fecha inicio", value=last_week, min_value=pd.Timestamp(year=2023, month=2, day=14),
                          max_value=pd.Timestamp.now()))  # default to last week

    with fin:
        fecha_fin = str(st.date_input(label="Fecha fin", value=pd.Timestamp.now(), max_value=pd.Timestamp.now(),
                                      min_value=fecha_ini))

    return fecha_ini, fecha_fin


def element_filter():
    elements = ["lluvia", "temperatura", "viento", "humedad"]

    st.markdown("<br><p style='text-align: center;'>Selecciona los elementos a visualizar:</h3>",
                unsafe_allow_html=True)
    container = st.container()
    with container:
        selection = st.pills(
            "Elementos",
            options=elements,
            selection_mode="multi",
            label_visibility="collapsed"
        )

    container.markdown(
        """
        <style>
            [data-testid="stPillsFlex"] {
                justify-content: center;
                padding: 0 -10rem;
            }
            div.stButtonGroup {
                display: flex;
                justify-content: center;
            }
            
            div[aria-label="Button group"] {
                justify-content: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    return selection