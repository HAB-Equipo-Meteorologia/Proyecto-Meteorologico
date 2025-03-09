import streamlit as st

with open('resources/markdown/ML Preprocessing.md', "r") as f:
    intro_content = f.read()

intro, gru, prophet, simple_rnn = st.tabs(["Introducción", "GRU", "Prophet", "SimpleRNN"])

intro.markdown(intro_content, unsafe_allow_html=True)

gru.markdown("""
## Modelo Gated Recurrent Unit (GRU)

El modelo GRU es una variante de las redes neuronales recurrentes (RNN) que intenta resolver el problema de la desaparición del gradiente. A diferencia de las RNN tradicionales, las GRU tienen una estructura más simple y solo tienen dos puertas: una de reinicio y otra de actualización. Estas puertas permiten que las GRU "olviden" o "recuerden" información de manera más eficiente que las RNN tradicionales.

""")

gru.markdown(
    """ ##### Para la implementación de este modelo, se ha utilizado la librería de Keras. A continuación, se muestra un resumen de los resultados obtenidos""")

gru.markdown("""---""")

gru.markdown(
    """
    ### Métricas de Evaluación
    | MSE | MAE | RMSE | R2 |
    | --- | --- | --- | --- |
    | 0.004346 | 0.050778 | 0.065923 | 0.7276359 |
    """
)

gru.markdown("""---""")

gru.markdown(
    """
    ### Análisis de Residuos
    En la siguiente imagen se muestra un análisis de comparación entre los valores reales y los valores predichos por el modelo GRU:
    """
)

gru.image("resources/images/gru_comparison_analysis.png", caption="GRU Residual Analysis")

gru.markdown("""---""")

gru.markdown(
    """
    ### Histograma de Error
    En la siguiente imagen se muestra el histograma de los errores residuales del modelo GRU:
    """
)

gru.image("resources/images/gru_prediction_error_histogram.png", caption="GRU Prediction Error Histogram")

gru.markdown("""---""")

gru.markdown(
    """
    ### Historial de Entrenamiento
    En la siguiente imagen se muestra el historial de las métricas durante el entrenamiento del modelo GRU:
    """
)

gru.image("resources/images/gru_training_history.png", caption="GRU Training History")


prophet.markdown("""
## Modelo Prophet

El modelo Prophet es un modelo de series temporales desarrollado por Facebook que está diseñado para ser fácil de usar y ajustarse a una amplia variedad de conjuntos de datos. Prophet es capaz de manejar tendencias no lineales, efectos estacionales y días festivos, y también es robusto a los valores atípicos.

""")

prophet.markdown("""---""")

prophet.markdown(
    """
    ### Análisis de Residuos
    En la siguiente imagen se muestra un análisis de comparación entre los valores reales y los valores predichos por el modelo Prophet:
    """
)

prophet.image("resources/images/prophet_comparison_analysis.png", caption="Prophet Residual Analysis")

prophet.markdown("""---""")

prophet.markdown(
    """
    ### Histograma de Error
    En la siguiente imagen se muestra el histograma de los errores residuales del modelo Prophet:
    """
)

prophet.image("resources/images/prophet_prediction_error_histogram.png", caption="Prophet Prediction Error Histogram")

prophet.markdown("""---""")