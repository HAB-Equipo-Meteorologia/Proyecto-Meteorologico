from functools import reduce
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from src.api.routes.db_routes import elements
from helpers import api
from src.streamlit_app.components import filters
from src.streamlit_app.components.maps import estacion_map

TAG = "historical_estacion"
data = st.session_state[f"{TAG}_data"] if f"{TAG}_data" in st.session_state else None

fig = go.Figure()

with st.columns([1, 3, 1])[1]:
    com_id, prov_id, idema = filters.estacion_filter()
    st.session_state[f"{TAG}_idema"] = idema

    estacion_map(fig, idema)
    fecha_ini, fecha_fin = filters.date_range_filter()

    st.session_state[f"{TAG}_fecha_ini"] = fecha_ini
    st.session_state[f"{TAG}_fecha_fin"] = fecha_fin

with st.columns([1, 3, 1])[1]:
    st.plotly_chart(fig, use_container_width=True)
    selected_elements = filters.element_filter()

st.markdown("<br>", unsafe_allow_html=True)


def show_data():
    dfs = {}
    for k, v in data.items():
        dfs[k] = pd.DataFrame(v)

    if len(data) > 0 and len(selected_elements) > 0:
        dfs = {k: v for k, v in dfs.items() if k in selected_elements}
        st.success("Datos obtenidos correctamente")
        df = reduce(lambda left, right: pd.merge(
            left,
            right.drop(columns=left.columns.intersection(right.columns).difference(['uuid'])),
            on='uuid'
        ), [dfs[i] for i in selected_elements])
        df.sort_values(by='fecha', inplace=True)
        df = df[df['idema'] == idema]
        df = df.drop(columns=['uuid', 'extracted', 'idema'])

        st.markdown(
            """
            <style>
                [data-testid="stDataFrameResizable"] {
                    max-width: fit-content;
                    margin: auto;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.dataframe(df, hide_index=True, use_container_width=False)


def fetch_historical():
    _data = {}
    for element in elements:
        _data[element] = api.get_estaciones_historico(element, fecha_ini, fecha_fin)
    st.session_state[f"{TAG}_data"] = _data


def data_changed():
    return (
            st.session_state[f"{TAG}_idema"] != st.session_state.get(f"{TAG}_prev_idema", None) or
            st.session_state[f"{TAG}_fecha_ini"] != st.session_state.get(f"{TAG}_prev_fecha_ini", None) or
            st.session_state[f"{TAG}_fecha_fin"] != st.session_state.get(f"{TAG}_prev_fecha_fin", None)
    )


def update_session_state():
    st.session_state[f"{TAG}_prev_idema"] = st.session_state[f"{TAG}_idema"]
    st.session_state[f"{TAG}_prev_fecha_ini"] = st.session_state[f"{TAG}_fecha_ini"]
    st.session_state[f"{TAG}_prev_fecha_fin"] = st.session_state[f"{TAG}_fecha_fin"]


if data is None or data_changed():
    with st.spinner("Obteniendo datos..."):
        fetch_historical()
        update_session_state()
    st.rerun()
else:
    show_data()
