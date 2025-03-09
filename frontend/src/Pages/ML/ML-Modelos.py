import io
import os
from datetime import datetime, timedelta
import joblib
import pandas as pd
import numpy as np
import requests
import streamlit as st
from keras.api.models import load_model
from common.config import script_dir
from helpers.lookups import prov_names, provincia_lookup, estacion_lookup, estaciones
from backend.src.ml_scripts import impute
from backend.src.ml_scripts import clean, scale
from backend.src.ml_scripts import create_sequences
from backend.src.ml_scripts import plot_forecast

model_path = os.path.join(script_dir, '../ml/models')
scaler_path = os.path.join(script_dir, '../ml/scalers')

if "ml_first_run" not in st.session_state:
    st.session_state.ml_first_run = True

columns = ['fecha', 'idema', 'tmed', 'prec', 'tmin', 'tmax', 'hr_max','hr_media']

@st.cache_resource
def load_gru():
    return load_model(os.path.join(model_path, 'gru.keras'))


@st.cache_resource
def load_prophet():
    url = "https://rednvrsdcuwtwyfxtjru.supabase.co/storage/v1/object/public/ml//prophet.joblib"

    try:
        response = requests.get(url, timeout=20)

        if response.status_code == 200:
            try:
                model = joblib.load(io.BytesIO(response.content))
                return model
            except Exception as e:
                st.error(f"Error al cargar el modelo Prophet: {str(e)}")
        else:
            st.error(f"Error al descargar el modelo Prophet: {response.status_code}")

    except Exception as e:
        st.error(f"Error al descargar el modelo Prophet: {str(e)}")

    return None


@st.cache_resource
def load_scalers():
    _scaler_X = joblib.load(os.path.join(scaler_path, 'scaler_X_train.joblib'))
    _scaler_y = joblib.load(os.path.join(scaler_path, 'scaler_y_train.joblib'))

    return _scaler_X, _scaler_y

gru = load_gru()
prophet = load_prophet()

scaler_X, scaler_y = load_scalers()


def predict_gru():
    df_scaled = df.copy()
    df_scaled = df_scaled.set_index('fecha')
    df_scaled = scale.scale_df(df_scaled, scaler_X, scaler_y)

    target = 'tmed'

    X = df_scaled.drop(columns=[target])
    y = df_scaled[target]

    X_seq, y_seq, dates_seq = create_sequences(X, y, df_scaled.index)

    y_pred = gru.predict(X_seq)
    y_pred_inverse = scaler_y.inverse_transform(y_pred).flatten()

    future_dates = []

    if isinstance(dates_seq[0], (list, np.ndarray)):
        for date_sequence in dates_seq:
            last_date = date_sequence[-1]
            if isinstance(last_date, pd.Timestamp):
                future_dates.append(last_date + pd.Timedelta(days=1))
            else:
                future_dates.append(pd.Timestamp(last_date) + pd.Timedelta(days=1))
    else:
        last_date = df_scaled.index[-1]
        future_dates = [last_date + pd.Timedelta(days=i + 1) for i in range(len(y_pred_inverse))]

    return pd.DataFrame({
        'fecha': future_dates,
        'tmed': y_pred_inverse
    })


def predict_prophet():
    days_ahead = len(df['fecha'].unique())-7
    last_historical_date = df['fecha'].max()

    future_dates = pd.date_range(
        start=last_historical_date + pd.Timedelta(days=1),
        periods=days_ahead,
        freq='D'
    )

    future = pd.DataFrame({'ds': future_dates})

    forecast = prophet.predict(future)

    return pd.DataFrame({
        'fecha': forecast['ds'],
        'tmed': forecast['yhat']
    })


def make_prediction():
    df_gru = predict_gru()
    df_prop = predict_prophet()
    df_hist = pd.DataFrame({
        'fecha': df['fecha'],
        'tmed': df['tmed']
    })

    # add the last date from hist onto start of gru and prop
    df_gru = pd.concat([df_hist.tail(1), df_gru])
    df_prop = pd.concat([df_hist.tail(1), df_prop])

    result = df_hist.rename(columns={'tmed': 'historical_tmed'})

    result = pd.merge(
        result,
        df_gru.rename(columns={'tmed': 'gru_tmed'}),
        on='fecha',
        how='outer'
    )

    result = pd.merge(
        result,
        df_prop.rename(columns={'tmed': 'prop_tmed'}),
        on='fecha',
        how='outer'
    )

    result = result.sort_values('fecha')

    predict_start = df['fecha'].values[-1]

    fig = plot_forecast(result, predict_start)

    st.plotly_chart(fig)

offset_map = {
    '1W': 7,
    '1M': 30,
    '3M': 90,
    '6M': 180,
    '1Y': 365,
    '2Y': 730,
    '5Y': 1825
}

tiempo_prediccion = st.pills(options=offset_map.keys(), label='Rango predicción', key="rango", default='1W')

fecha_final = datetime.now().strftime('%Y-%m-%d')

fecha_inicial = (datetime.now() - timedelta(days=offset_map[tiempo_prediccion]+10)).strftime('%Y-%m-%d')

with st.sidebar:

    provincia = st.selectbox("Selecciona la provincia", prov_names[1:])
    prov_id = provincia_lookup[provincia]

    filtered_idemas = [idema for idema, value in estaciones.items() if str(value['provincia_id']) == str(prov_id)]
    est_names = [estaciones[idema]['nombre'] for idema in filtered_idemas]
    estacion = st.selectbox("Selecciona la estación", est_names)
    idema = [estacion_lookup[estacion]]


    if st.button("Aplicar") or st.session_state.ml_first_run or tiempo_prediccion != st.session_state.tiempo_prediccion:
        st.session_state.ml_first_run = False
        st.session_state.tiempo_prediccion = tiempo_prediccion

        with st.spinner("Cargando datos..."):
            st.session_state.ml_data = api.get_historico(
                columns=columns,
                idemas=idema,
                fecha_ini=fecha_inicial,
                fecha_fin=fecha_final
            )

if 'ml_data' not in st.session_state:
    st.header("Aplique los filtros para cargar los datos.")
    st.stop()

data = st.session_state.ml_data

if len(data) == 0:
    st.error("No hay datos disponibles para el rango seleccionado.")
else:
    df = pd.DataFrame(data)
    df = clean.clean_df(df)
    df = impute.impute_knn(df)

    make_prediction()