from functools import reduce
import streamlit as st
import pandas as pd
from folium import Map, Marker
from streamlit_folium import st_folium
from src.streamlit import requester
from src.streamlit.config import com_names, provincias, estaciones, \
    comunidad_lookup, provincia_lookup, estacion_lookup

with open("src/streamlit/styles/default.css") as f:
    css = f.read()

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

with st.columns([1,3,1])[1]:

    comunidad = st.selectbox("Selecciona la comunidad autónoma", com_names)
    com_id = comunidad_lookup[comunidad]

    prov_names = [provincias[index]["nombre"] for index in provincias if str(provincias[index]["com_auto_id"]) == com_id]
    provincia = st.selectbox("Selecciona la provincia", prov_names)
    prov_id = provincia_lookup[provincia]

    est_names = [estaciones[index]["nombre"] for index in estaciones if str(estaciones[index]["provincia_id"]) == prov_id]
    estacion = st.selectbox("Selecciona la estación meteorológica", est_names)
    idema = estacion_lookup[estacion]

    _, ini, _, fin, _ = st.columns([2,5,2,5,2])
    last_week = pd.Timestamp.now() - pd.DateOffset(weeks=2)

    with ini:
        fecha_ini = str(st.date_input(label="Fecha inicio", value=last_week, min_value=pd.Timestamp(year=2023, month=2, day=14), max_value=pd.Timestamp.now())) # default to last week

    with fin:
        fecha_fin = str(st.date_input(label="Fecha fin", value=pd.Timestamp.now(), max_value=pd.Timestamp.now(), min_value=fecha_ini)) # default to today

with st.columns([1,3,1])[1]:

    est_lat = estaciones[idema]["latitud"]
    est_long = estaciones[idema]["longitud"]

    m = Map(location=[est_lat, est_long+2.5], zoom_start=7)
    Marker(location=[est_lat, est_long], popup=estacion).add_to(m)
    st_folium(m, height = 300, width=800)

    elements = ["lluvia", "temperatura", "viento", "humedad"]

    st.markdown("<br><p style='text-align: center;'>Selecciona los elementos a visualizar:</h3>", unsafe_allow_html=True)
    selection = st.pills(
        "",
        options=elements,
        selection_mode="multi",
    )

    st.markdown("<br>", unsafe_allow_html=True)

endpoint = "/db/historico/estacion/{idema}/{elemento}/rango/{fecha_ini}/{fecha_fin}"

dfs = []

for element in selection:
    data = requester.get_request(endpoint.format(elemento=element, idema=idema, fecha_ini=fecha_ini, fecha_fin=fecha_fin))

    if data is None:
        st.error("Error al obtener los datos")

    if len(data) == 0:
        st.error("No hay datos disponibles para el rango de fechas seleccionado")
        break

    dfs.append(pd.DataFrame(data))

if dfs:
    st.success("Datos obtenidos correctamente")
    df = reduce(lambda left, right: pd.merge(
        left,
        right.drop(columns=left.columns.intersection(right.columns).difference(['uuid'])),
        on='uuid',
        how='inner'
    ), dfs)
    df.sort_values(by='fecha', inplace=True)
    df = df.drop(columns=['uuid', 'extracted', 'idema'])

    with st.columns([1, 2, 1])[1]:
        st.dataframe(df, hide_index=True)
