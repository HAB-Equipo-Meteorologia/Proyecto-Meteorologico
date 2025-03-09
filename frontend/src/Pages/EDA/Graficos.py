import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from frontend.src.plots.plotly import histograms, scatter_matrix, time_series
from frontend.src.components.filters import date_range_filter
from frontend.src.components.tabs import element_tabs
from frontend.src.services.resources import ResourceManager
from frontend.src.services import api_client

res = ResourceManager()

if "first_run" not in st.session_state:
    st.session_state.first_run = True

st.title("Análisis Exploratorio de Datos :chart_with_upwards_trend:")

element_tabs()
selected_element = st.session_state.selected_element

def show_graphs():
    show_daily_average()
    show_histograms()
    show_scatter_matrix()

def show_histograms():
    st.header("Histogramas")

    if not data:
        st.error("No hay datos disponibles para el rango seleccionado.")
        return

    columns = res.numeric_columns[selected_element]

    if st.checkbox("Logaritmo", key=f"{selected_element}_log_histogram"):
        selected_df = avg_df_log
    else:
        selected_df = avg_df

    colors = [res.histogram_color_maps[col] for col in columns]

    hist = histograms(
        selected_df,
        title=f"{selected_element.upper()}",
        cols=res.numeric_columns[selected_element],
        x_label=selected_element,
        colors=colors
    )
    st.plotly_chart(hist, use_container_width=True)

def show_scatter_matrix():
    st.header("Scatter Matrix")

    x_cols = res.numeric_columns[selected_element]
    y_cols = [col for col in res.scatter_color_maps.keys() if col not in x_cols]

    x_col_labels = [res.column_labels[col] for col in x_cols]
    y_col_labels = [res.column_labels[col] for col in y_cols]
    
    dfs = []

    for col in numeric_cols:
        df_var = avg_df[['provincia_id', 'fecha', col]]
        dfs.append(df_var)

    trendlines = st.checkbox("Trendlines", key=f"{selected_element}_trendlines", value=True)

    if st.checkbox("Logaritmo", key=f"{selected_element}_log_scatter"):
        selected_df = avg_df_log
    else:
        selected_df = avg_df

    fig = scatter_matrix(
        selected_df,
        title="Scatter Matrix de Variables Meteorológicas",
        x_cols=x_cols,
        y_cols= y_cols,
        x_labels=x_col_labels,
        y_labels=y_col_labels,
        color=res.scatter_color_maps[selected_element],
        trendline=trendlines
    )

    st.plotly_chart(fig, use_container_width=True)

def show_daily_average():
    st.header("Promedio diario")
    daily_avg = avg_df.drop(columns=["provincia_id"]).groupby(["fecha"]).mean().reset_index()

    if st.checkbox("MinMax", key=f"{selected_element}_minmax"):
        scaler = MinMaxScaler()
        daily_avg[numeric_cols] = scaler.fit_transform(daily_avg[numeric_cols])

    columns = res.numeric_columns[selected_element]
    df_element = daily_avg[["fecha"] + columns]

    fig = time_series(
        df_element,
        title=f"{selected_element.capitalize()}",
        cols=columns,
        colors=[res.histogram_color_maps[col] for col in columns],
        x_label="Fecha",
        y_label=selected_element
    )

    st.plotly_chart(fig, use_container_width=True)

data = None

with st.sidebar:
    fecha_inicial, fecha_final = date_range_filter('gráficos')
    provincia = st.selectbox("Selecciona la provincia", provincias)
    prov_id = api_client.lookup_provincia[provincia]

    if st.button("Aplicar") or st.session_state.first_run:
        st.session_state.first_run = False

        with st.spinner("Cargando datos..."):
            st.session_state.graficos_data = api_client.get_historico_average(
                provincia_ids=[prov_id] if prov_id else None,
                fecha_ini=fecha_inicial,
                fecha_fin=fecha_final
            )

if 'graficos_data' not in st.session_state:
    st.header("Aplique los filtros para cargar los datos.")
    st.stop()

data = st.session_state.graficos_data

if len(data) == 0:
    st.error("No hay datos disponibles para el rango seleccionado.")
else:
    avg_df = pd.DataFrame(data).drop(columns=['extracted'])
    avg_df['provincia_id'] = avg_df['provincia_id'].astype(str)
    avg_df = avg_df[avg_df['provincia_id'] == prov_id] if prov_id != "0" else avg_df

    avg_df_log = avg_df.copy(deep=True)
    avg_df_log = api_client.log_transform_df(avg_df_log, numeric_cols)

    show_graphs()
