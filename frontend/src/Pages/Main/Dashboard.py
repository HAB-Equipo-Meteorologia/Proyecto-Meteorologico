import streamlit as st


st.title('Análisis Meteorológico :lightning:')

st.markdown("""
#### ¡Bienvenidas y bienvenidos a nuestra aplicación de análisis meteorológico! 
            
Para este proyecto, hemos desarrollado una aplicación web que permite navegar y visualizar de manera cómoda y sencilla los datos meteorológicos extraídos de la [AEMET](https://opendata.aemet.es/dist/index.html). Hemos creado una base de datos para almacenar eficientemente la información extraída y hemos diseñado un proceso ETL para manternerla actualizada.
""")

st.markdown("""
Si seleccionas las páginas en el menú de la izquierda, podrás acceder a las diferentes secciones de la aplicación en las que encontrarás:  
            
* **Principal**: página principal de la aplicación, presentación del equipo y contacto.  

* **Análisis Exploratorio de Datos**: visualizaciones gráficas de los principales datos meteorológicos (temperatura, lluvia, viento, humedad, presión atmosférica y horas de sol). También podrás encontrar un mapa coroplético para visualizar estos mismos datos por provincia.  

* **Machine Learning**: predicciones de la temperatura para un periodo y una ubicación concretas utilizando diferentes modelos de machine learning.

""")

st.markdown("""""")

st.markdown("""
Si quieres acceder a nuestro código, puedes hacerlo a través de nuestro repositorio en GitHub:
""")
st.link_button('Repositorio GitHub', 'https://github.com/HAB-Equipo-Meteorologia/Proyecto-Meteorologico')

st.markdown("""---""")
