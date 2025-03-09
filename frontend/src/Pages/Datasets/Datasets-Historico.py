import streamlit as st
import pandas as pd
import requests
from io import StringIO

BASE_URL = "https://rednvrsdcuwtwyfxtjru.supabase.co/storage/v1/object/public/historical"

years = list(range(1997, 2026))

st.title("📚 Datasets Históricos de la AEMET")
st.markdown("Datos meteorológicos históricos para España de los años 1997-2025 extraídos de AEMET.")

tab1, tab2, tab3 = st.tabs(["Navegador de Archivos", "Previsualización de Datos", "Comparador de Años"])

with tab1:
    st.header("Archivos Disponibles")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Datos Históricos ('historico')")
        for year in years:
            file_url = f"{BASE_URL}/historico/{year}.csv"
            with st.expander(f"{year}.csv"):
                st.write(f"Datos historicos para el año {year}")
                st.markdown(f"[Descargar {year}.csv]({file_url})")

    with col2:
        st.subheader("Media de Datos Historicos por Provincia ('historico_avg')")
        for year in years:
            file_url = f"{BASE_URL}/historico_avg/{year}.csv"
            with st.expander(f"{year}.csv"):
                st.write(f"Datos historicos por provincia para el año {year}")
                st.markdown(f"[Descargar {year}.csv]({file_url})")

with tab2:
    st.header("Previsualización de Datos")

    data_category = st.radio("Seleccionar categoría:", ["historico", "historico_avg"])
    selected_year = st.select_slider("Seleccionar Año:", years)

    selected_url = f"{BASE_URL}/{data_category}/{selected_year}.csv"

    if st.button("Previsualizar Datos"):
        try:
            st.info(f"Cargando preview para {data_category}/{selected_year}.csv...")

            response = requests.get(selected_url)

            if response.status_code == 200:
                data = pd.read_csv(StringIO(response.text))

                st.subheader("Estadísticas")
                st.write(data.describe())

                st.subheader("Información de Columnas")
                col_info = pd.DataFrame({
                    'Columna': data.columns,
                    'Data Type': data.dtypes.values,
                    'Non-Null Count': data.count().values,
                    'Null Count': data.isna().sum().values
                })
                st.write(col_info)

                st.subheader(f"Muestra de {selected_year}")
                st.write(data.head(10))
            else:
                st.error(f"Error en cargar. Status code: {response.status_code}")
        except Exception as e:
            st.error(f"Error al intentar previsualizar: {str(e)}")

with tab3:
    st.header("Comparador de Años")

    compare_category = st.radio("Selecciona la categoría:", ["historico", "historico_avg"],
                                key="compare_category")

    compare_years = st.multiselect("Selecciona los años a comparar:", years, default=[years[-1], years[-2]])

    if st.button("Comparar Años"):
        if len(compare_years) < 1:
            st.warning("Por favor seleccione al menos un año para comparar.")
        else:
            try:
                all_data = {}

                for year in compare_years:
                    url = f"{BASE_URL}/{compare_category}/{year}.csv"
                    response = requests.get(url)

                    if response.status_code == 200:
                        df = pd.read_csv(StringIO(response.text))
                        all_data[year] = df
                    else:
                        st.error(f"Error en cargar año {year}. Status code: {response.status_code}")

                if all_data:
                    if len(all_data) > 1:
                        st.subheader("Comparación de Años Seleccionados")

                        for year, df in all_data.items():
                            st.write(f"**Resumen de {year}:**")
                            st.write(df.describe())
                            st.write("---")

                    st.subheader("Datos individuales para cada año (primeras 5 filas)")
                    for year, df in all_data.items():
                        st.write(f"**{year}**")
                        st.write(df.head(5))
                        st.write("---")

            except Exception as e:
                st.error(f"Error al comparar años: {str(e)}")

st.markdown("---")
