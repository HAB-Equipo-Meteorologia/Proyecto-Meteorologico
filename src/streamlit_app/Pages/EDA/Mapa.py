import folium
import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from streamlit_folium import folium_static
from helpers import api
from helpers.lookups import element_cols_map_numeric, label_maps, choropleth_color_maps, provincias, \
    histogram_color_maps
from helpers.lookups import numeric_cols
from helpers.maps.folium import create_tooltip, get_column_choropleth
from helpers.maps.geojson import inject_col_values, geodata_provincias
from helpers.preprocessing import convert_numeric
from helpers.visualization import bar_plots
from src.streamlit_app.components.filters import date_range_filter
from src.streamlit_app.components.tabs import element_tabs

if "mapa_first_run" not in st.session_state:
    st.session_state.mapa_first_run = True

st.title("Mapa Coroplético :world_map:")

element_tabs()
selected_element = st.session_state.selected_element

geojson = st.session_state.geojson if 'geojson' in st.session_state else None
mapa_data = st.session_state.mapa_data if 'mapa_data' in st.session_state else None
avg_df = st.session_state.avg_df if 'avg_df' in st.session_state else None

def show_choropleth_map():

    if st.session_state.selected_element:

        if st.checkbox("Canarias", key="canarias"):
            location = [36, -7]
            zoom_start = 5
        else:
            location = [40, -3]
            zoom_start = 6

        maps = {}

        for col in element_cols_map_numeric[selected_element]:

            maps[col] = folium.Map(
                location=location,
                zoom_start=zoom_start,
                zoom_control=False,
                control_scale=False,
                tiles=None
            )

            folium.TileLayer(
                tiles='https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png',
                attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                name='Land Only',
                overlay=True
            ).add_to(maps[col])

            choro = get_column_choropleth(st.session_state.geojson, avg_df, col, label_maps[col], choropleth_color_maps[col]).add_to(maps[col])
            create_tooltip(col, label_maps[col]).add_to(choro.geojson)

        columns = list(maps.keys())
        col_labels = [label_maps[col] for col in columns]

        selected_label = st.radio(
            label="Selecciona el variable:",
            options=col_labels,
            label_visibility="hidden",
            horizontal=True
        )
        selected_map = columns[col_labels.index(selected_label)]

        folium_static(maps[selected_map], width=900, height=550)

def show_histogram_provincias():

    cols = element_cols_map_numeric[selected_element]

    avg_df['provincia'] = avg_df['provincia_id'].apply(lambda x: provincias[x]['nombre'])

    sorted_data = avg_df.groupby('provincia')[cols].mean().sort_values(by=cols[0])

    if st.checkbox("MinMax", key=f"{selected_element}_minmax"):
        scaler = MinMaxScaler()
        sorted_data[cols] = scaler.fit_transform(sorted_data[cols])

    fig = bar_plots(
        sorted_data,
        title=f"{selected_element.capitalize()} por Provincia",
        cols=cols,
        x_label="Provincia",
        y_label="Valor promedio",
        label_maps=label_maps,
        colors=[histogram_color_maps[col] for col in cols]
    )

    st.plotly_chart(fig, use_container_width=True)

with st.sidebar:
    fecha_inicial, fecha_final = date_range_filter('mapa')

    if st.button("Aplicar") or st.session_state.mapa_first_run:
        st.session_state.mapa_first_run = False

        with st.spinner("Cargando datos..."):
            st.session_state.mapa_data = api.get_historico_average(
                fecha_ini=fecha_inicial,
                fecha_fin=fecha_final
            )

        _avg_df = pd.DataFrame(st.session_state.mapa_data).drop(columns=["extracted"])
        _avg_df['provincia_id'] = _avg_df['provincia_id'].astype(str)
        _avg_df = convert_numeric(_avg_df, numeric_cols)
        _avg_df = _avg_df[_avg_df['provincia_id'] != '0']

        _geojson = geodata_provincias.copy()

        for element in element_cols_map_numeric.keys():
            st.write(element)
            inject_col_values(_geojson, _avg_df, element_cols_map_numeric[element])

        st.session_state.geojson = _geojson
        st.session_state.avg_df = _avg_df

        st.rerun()


if geojson is None or mapa_data is None or avg_df is None:
    st.header("Aplique los filtros para cargar los datos.")
    st.stop()

if len(st.session_state.mapa_data) == 0:
    st.error("No hay datos disponibles para el rango seleccionado.")
    st.stop()

show_choropleth_map()
show_histogram_provincias()
