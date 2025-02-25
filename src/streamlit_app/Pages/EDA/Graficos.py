import sys
import streamlit as st
import pandas as pd
import unidecode
import plotly.express as px
from functools import reduce

sys.path.append('../..')

from src.db.db_handler import DBHandler
from helpers.visualization import histograma
from helpers.coropleth_map import unificar_geojson_provincias, merge_geojson_provincias, crear_mapa_choropleth
from streamlit_folium import st_folium


from src.streamlit_app.components.filters import select_variable, select_date

def show_graficos():
    st.title("Análisis Exploratorio de Datos")
    

    opcion = select_variable(
        ["Histogramas", "Scatter Matrix", "Mapa Coroplético"],
        label="Selecciona la visualización:"
    )
    
    if opcion == "Histogramas":
        graficar_histogramas()
    elif opcion == "Scatter Matrix":
        graficar_scatter_matrix()
    elif opcion == "Mapa Coroplético":
        mapa_coropletico()

def graficar_histogramas():
    st.header("Histogramas")
    
    db = DBHandler()
    df_estaciones = pd.DataFrame(db.get_table("estaciones"))
    df_provincias = pd.DataFrame(db.get_table("provincias"))
    

    variables_histograma = {
        "Temperatura Media (°C)": ("temperatura", "temperatura_historico", "tmed"),
        "Velocidad Media del Viento (m/s)": ("viento", "viento_historico", "velmedia"),
        "Precipitaciones (mm)": ("lluvia", "lluvia_historico", "prec"),
        "Humedad Relativa Media (%)": ("humedad", "humedad_historico", "hr_media")
    }
    

    variable_seleccionada = select_variable(
        list(variables_histograma.keys()),
        label="Selecciona una variable:"
    )
    elemento, tabla, columna = variables_histograma[variable_seleccionada]
    
    fecha_inicial = db.get_earliest_historical_date(tabla)
    fecha_fin = db.get_latest_historical_date(tabla)
    data = db.get_estaciones_historico_rango(elemento, fecha_inicial, fecha_fin)
    
    df = pd.DataFrame(data).merge(df_estaciones, on="idema", how="left").merge(
        df_provincias, left_on="provincia_id", right_on="id", how="left", suffixes=("_est", "_prov")
    ).sort_values("fecha")
    
    if columna in df.columns:
        fig = histograma(
            df,
            title=f"Histograma de {variable_seleccionada}",
            col=columna,
            x_label=variable_seleccionada
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"La columna {columna} no está disponible en los datos.")

def graficar_scatter_matrix():
    st.header("Scatter Matrix")
    
    db = DBHandler()
    df_estaciones = pd.DataFrame(db.get_table("estaciones"))
    df_provincias = pd.DataFrame(db.get_table("provincias"))
    
    variables_info = {
        "tmed": ("temperatura", "temperatura_historico"),
        "velmedia": ("viento", "viento_historico"),
        "prec": ("lluvia", "lluvia_historico"),
        "hrMedia": ("humedad", "humedad_historico")
    }
    
    dfs = []
    for var, (elemento, tabla) in variables_info.items():
        fecha_inicial = db.get_earliest_historical_date(tabla)
        fecha_final = db.get_latest_historical_date(tabla)
        data = db.get_estaciones_historico_rango(elemento, fecha_inicial, fecha_final)
        df_var = pd.DataFrame(data)[['idema', 'fecha', var]]
        dfs.append(df_var)
    
    df_merged_vars = reduce(
        lambda left, right: pd.merge(left, right, on=['idema', 'fecha'], how='outer'),
        dfs
    )
    df_merged = df_merged_vars.merge(df_estaciones, on="idema", how="left").merge(
        df_provincias, left_on="provincia_id", right_on="id", how="left", suffixes=("_est", "_prov")
    )
    
    variables = ["tmed", "velmedia", "prec", "hrMedia"]
    if all(var in df_merged.columns for var in variables):
        fig_scatter = px.scatter_matrix(df_merged, dimensions=variables)
        fig_scatter.update_traces(marker=dict(color="purple", size=6, opacity=0.7))
        fig_scatter.update_layout(
            title="Scatter Matrix de Variables Meteorológicas",
            width=1300,
            height=1300
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.error("No se pueden visualizar todas las variables en el Scatter Matrix.")

def mapa_coropletico():
    st.header("Mapa Coroplético de la temperatura media por provincia")
    

    fecha_temp = str(select_date())
    
    db = DBHandler()
    temp_data = db.get_estaciones_historico_rango("temperatura", fecha_temp, fecha_temp)
    
    provincias = db.get_table("provincias")
    estaciones = db.get_table("estaciones")
    
    df_provincias = pd.DataFrame(provincias)
    df_estaciones = pd.DataFrame(estaciones)
    df_temp = pd.DataFrame(temp_data)
    
    df_temp_merged = df_temp.merge(df_estaciones, on="idema", how="left").merge(
        df_provincias, left_on="provincia_id", right_on="id", how="left", suffixes=("_est", "_prov")
    ).sort_values("fecha")
    
    df_temp_prov = df_temp_merged.groupby("provincia_id", as_index=False).agg({
        "nombre_prov": "last",
        "tmed": "mean"
    })
    df_temp_prov["nombre_prov"] = df_temp_prov["nombre_prov"].apply(
        lambda x: unidecode.unidecode(x.strip().lower())
    )
    
    geojson_dir = "../../data/geojson/provincias"
    geojson_unificado = unificar_geojson_provincias(geojson_dir)
    geojson_merged = merge_geojson_provincias(geojson_unificado)
    
    df_temp_prov["provincia_id"] = df_temp_prov["provincia_id"].astype(str)
    
    mapa = crear_mapa_choropleth(
        geojson_data=geojson_merged,
        df=df_temp_prov,
        id_col="provincia_id",
        value_col="tmed",
        tooltip_field=["nombre_prov", "tmed"],
        tooltip_alias=["Provincia:", "Temperatura media (°C):"],
        legend_name="Temperatura Media (°C)"
    )
    
    st_folium(mapa, width=700, height=500)


if "st_page" in globals():
    show_graficos()
