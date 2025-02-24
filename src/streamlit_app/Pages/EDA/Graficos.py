import sys
import streamlit as st
import pandas as pd
import unidecode
import plotly.express as px
from functools import reduce
from datetime import datetime

sys.path.append('../..')

from src.db.db_handler import DBHandler
from helpers.visualization import histograma
from helpers.coropleth_map import unificar_geojson_provincias, merge_geojson_provincias, crear_mapa_choropleth

from streamlit_folium import st_folium

def graficar_histogramas():
    db = DBHandler()
    df_estaciones = pd.DataFrame(db.get_table_data("estaciones"))
    df_provincias = pd.DataFrame(db.get_table_data("provincias"))
    
    st.header("Histogramas")
    

    fecha_inicial_temp = db.get_earliest_historical_date("temperatura_historico")
    fecha_fin_temp = db.get_latest_historical_date("temperatura_historico")
    data_temp = db.get_estaciones_historico("temperatura", fecha_inicial_temp, fecha_fin_temp)
    df_temp = pd.DataFrame(data_temp)
    df_temp_merged = df_temp.merge(df_estaciones, on="idema", how="left")
    df_temp_merged = df_temp_merged.merge(
        df_provincias,
        left_on="provincia_id",
        right_on="id",
        how="left",
        suffixes=("_est", "_prov")
    ).sort_values("fecha")
    fig_temp = histograma(df_temp_merged, "tmed", fecha_inicial_temp, fecha_fin_temp, "Temperatura Media (°C)")
    st.plotly_chart(fig_temp, use_container_width=True)
    st.write("**Análisis:** El histograma de Temperatura muestra la distribución de la temperatura media durante los últimos 2 años. Vemos que las temperaturas medias en este periodo en todo el territorio español han ido desde los -15°C a los 45°C, estando la mayoría de las temperaturas entre los 10°C y los 25°C. Tenemos una distribución bastante simétrica. Parece detectarse algún valor atípico en las colas.")
    

    fecha_inicial_viento = db.get_earliest_historical_date("viento_historico")
    fecha_fin_viento = db.get_latest_historical_date("viento_historico")
    data_viento = db.get_estaciones_historico("viento", fecha_inicial_viento, fecha_fin_viento)
    df_viento = pd.DataFrame(data_viento)
    df_viento_merged = df_viento.merge(df_estaciones, on="idema", how="left")
    df_viento_merged = df_viento_merged.merge(
        df_provincias,
        left_on="provincia_id",
        right_on="id",
        how="left",
        suffixes=("_est", "_prov")
    ).sort_values("fecha")
    fig_viento = histograma(df_viento_merged, "velmedia", fecha_inicial_viento, fecha_fin_viento, "Velocidad Media del Viento (m/s)")
    st.plotly_chart(fig_viento, use_container_width=True)
    st.write("**Análisis:** El histograma de la velocidad media del viento muestra la distribución de la velocidad media en los últimos 2 años. Vemos que va desde los 0 a los 25-30m/s. Esta distribución tiene una asimetría positiva (sesgo a la derecha), la mayoría de los datos se concentran entre 0 y 5m/s, siendo la velocidad más habitual entre 1 y 3m/s. Se aprecian valores en la cola derecha, pero podrían tratarse de valores atípicos, al darse con una menor frecuencia.")
    

    fecha_inicial_lluvia = db.get_earliest_historical_date("lluvia_historico")
    fecha_fin_lluvia = db.get_latest_historical_date("lluvia_historico")
    data_lluvia = db.get_estaciones_historico("lluvia", fecha_inicial_lluvia, fecha_fin_lluvia)
    df_lluvia = pd.DataFrame(data_lluvia)
    df_lluvia_merged = df_lluvia.merge(df_estaciones, on="idema", how="left")
    df_lluvia_merged = df_lluvia_merged.merge(
        df_provincias,
        left_on="provincia_id",
        right_on="id",
        how="left",
        suffixes=("_est", "_prov")
    ).sort_values("fecha")
    df_lluvia_merged["prec"] = pd.to_numeric(df_lluvia_merged["prec"], errors="coerce")
    fig_lluvia = histograma(df_lluvia_merged, "prec", fecha_inicial_lluvia, fecha_fin_lluvia, "Precipitaciones (mm)")
    st.plotly_chart(fig_lluvia, use_container_width=True)
    st.write("**Análisis:** El histograma de precipitaciones muestra la distribución de la lluvia en los últimos 2 años. Detectamos una mayor concentración de los datos en valores bajos, también con una asimetría positiva y sesgo a la derecha. La mayoría de las observaciones se encuentran en torno a los 0mm, la mayoría de los días observados (recordamos que estamos hablando de datos de todo el país) han presentado pocas precipitaciones. Vemos que el histograma tiene una cola a la derecha, con valores más elevados, llegando incluso a los 700mm. Esto podría deberse a algún valor atípico.")
    

    fecha_inicial_humedad = db.get_earliest_historical_date("humedad_historico")
    fecha_fin_humedad = db.get_latest_historical_date("humedad_historico")
    data_humedad = db.get_estaciones_historico("humedad", fecha_inicial_humedad, fecha_fin_humedad)
    df_humedad = pd.DataFrame(data_humedad)
    df_humedad_merged = df_humedad.merge(df_estaciones, on="idema", how="left")
    df_humedad_merged = df_humedad_merged.merge(
        df_provincias,
        left_on="provincia_id",
        right_on="id",
        how="left",
        suffixes=("_est", "_prov")
    ).sort_values("fecha")
    fig_humedad = histograma(df_humedad_merged, "hrMedia", fecha_inicial_humedad, fecha_fin_humedad, "Humedad Relativa Media (%)")
    st.plotly_chart(fig_humedad, use_container_width=True)
    st.write("**Análisis:** El histograma de Humedad muestra la distribución del porcentaje de humedad relativa media a lo largo de los últimos 2 años. Vemos que el rango principal en el que se encuentran los datos está entre el 60% y el 90%, detectándose la mayoría de los datos entre el 70% y el 80%. Los valores muy bajos, aunque sí se detectan bastantes valores entre 0 y 10%, son menos frecuentes, así como los muy altos en torno al 100%. La distribución tiene una ligera asimetría, con colas tanto a la izquierda como a la derecha, pero siendo bastante simétrica en torno al valor central. ")


def graficar_scatter_matrix():
    db = DBHandler()
    df_estaciones = pd.DataFrame(db.get_table_data("estaciones"))
    df_provincias = pd.DataFrame(db.get_table_data("provincias"))
    
    st.header("Scatter Matrix")
    
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
        data = db.get_estaciones_historico(elemento, fecha_inicial, fecha_final)
        df_var = pd.DataFrame(data)[['idema', 'fecha', var]]
        dfs.append(df_var)
    
    df_merged_vars = reduce(lambda left, right: pd.merge(left, right, on=['idema', 'fecha'], how='outer'), dfs)
    df_merged = df_merged_vars.merge(df_estaciones, on="idema", how="left")
    df_merged = df_merged.merge(
        df_provincias,
        left_on="provincia_id",
        right_on="id",
        how="left",
        suffixes=("_est", "_prov")
    )
    df_merged["prec"] = pd.to_numeric(df_merged["prec"], errors="coerce")
    df_merged = df_merged.sort_values("fecha")
    
    variables = ["tmed", "velmedia", "prec", "hrMedia"]
    df_plot = df_merged[variables]
    
    fig_scatter = px.scatter_matrix(df_plot, dimensions=df_plot.columns)
    fig_scatter.update_traces(marker=dict(color="mediumpurple", size=6, opacity=0.7))
    fig_scatter.update_layout(title="Pair Plot de Variables Meteorológicas", width=1300, height=1300)
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.write("**Análisis:** El scatter matrix permite identificar relaciones y correlaciones entre las variables meteorológicas que hemos estudiado en los histogramas. En general, la mayoría de las variables vemos que no parecen tener una relación clara. La mayoría de los gráficos de dispersión nos muestran una nube de puntos distribuída en todo el cuadrante. Sí que vemos, como cabría esperar, una relación positiva entre las precipitaciones y la humedad relativa media. A mayores precipitaciones, mayor será la humedad relativa. También detectamos una relación inversa entre la humedad relativa y la temperatura media, a mayor temperatura la humedad tiende a disminuir. En cuanto a la variable de velocidad media del viento, no parece tener una relación muy clara con el resto de las variables meteorológicas, aunque sí que detectamos una posible relación con las precipitaciones ya que la mayoría de las precipitaciones ocurren con vientos bajos. ")


def filtro_fecha_unica():
    fecha = st.date_input(
        "Selecciona una fecha para visualizar en el mapa",
        value=pd.Timestamp.now(),
        min_value=pd.Timestamp(year=2023, month=2, day=14),
        max_value=pd.Timestamp.now()
    )
    return str(fecha)


def mapa_coropletico():
    st.header("Mapa Coroplético de la temperatura media por provincia")
    
    fecha_temp = filtro_fecha_unica()
    
    db = DBHandler()
    temp_data = db.get_estaciones_historico("temperatura", fecha_temp, fecha_temp)
    
    provincias = db.get_table_data("provincias")
    estaciones = db.get_table_data("estaciones")
    
    df_provincias = pd.DataFrame(provincias)
    df_estaciones = pd.DataFrame(estaciones)
    df_temp = pd.DataFrame(temp_data)
    
    df_temp_merged = df_temp.merge(df_estaciones, on="idema", how="left")
    df_temp_merged = df_temp_merged.merge(
        df_provincias,
        left_on="provincia_id",
        right_on="id",
        how="left",
        suffixes=("_est", "_prov")
    ).sort_values("fecha")
    
    df_temp_prov = df_temp_merged.groupby("provincia_id", as_index=False).last()[["provincia_id", "nombre_prov", "tmed"]]

    df_temp_prov["nombre_prov"] = df_temp_prov["nombre_prov"].apply(lambda x: unidecode.unidecode(x.strip().lower()))
    
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
    st.write("**Análisis:** El mapa coroplético muestra la distribución de la temperatura media por provincia para la fecha seleccionada, permitiendo identificar patrones geográficos en la variabilidad de la temperatura. Los colores del mapa muestran valores azules cuanto menor sea la temperatura media y valores rojos cuanto mayor sea la misma.")


if __name__ == '__main__':
    graficar_histogramas()
    graficar_scatter_matrix()
    mapa_coropletico()
