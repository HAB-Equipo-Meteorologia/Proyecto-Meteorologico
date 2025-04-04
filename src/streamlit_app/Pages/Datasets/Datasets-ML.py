import streamlit as st

BASE_URL = "https://rednvrsdcuwtwyfxtjru.supabase.co/storage/v1/object/public/ml"

files = [
    {"name": "full.csv", "description": "Full dataset", "url": f"{BASE_URL}/full.csv"},
    {"name": "train.csv", "description": "Training dataset", "url": f"{BASE_URL}/train.csv"},
    {"name": "validation.csv", "description": "Validation dataset", "url": f"{BASE_URL}/validation.csv"},
    {"name": "test.csv", "description": "Testing dataset", "url": f"{BASE_URL}/test.csv"},

    {"name": "full_scaled.csv", "description": "Scaled full dataset", "url": f"{BASE_URL}/full_scaled.csv"},
    {"name": "train_scaled.csv", "description": "Scaled training dataset", "url": f"{BASE_URL}/train_scaled.csv"},
    {"name": "validation_scaled.csv", "description": "Scaled validation dataset", "url": f"{BASE_URL}/validation_scaled.csv"},
    {"name": "test_scaled.csv", "description": "Scaled testing dataset", "url": f"{BASE_URL}/test_scaled.csv"},

    {"name": "scaler_X_full.joblib", "description": "Scaler for X_full", "url": f"{BASE_URL}/scaler_X_full.joblib"},
    {"name": "scaler_y_full.joblib", "description": "Scaler for y_full", "url": f"{BASE_URL}/scaler_y_full.joblib"},
    {"name": "scaler_X_train.joblib", "description": "Scaler for X_train", "url": f"{BASE_URL}/scaler_X_train.joblib"},
    {"name": "scaler_y_train.joblib", "description": "Scaler for y_train", "url": f"{BASE_URL}/scaler_y_train.joblib"},

    {"name": "prophet.pkl", "description": "Modelo Prophet", "url": f"{BASE_URL}/prophet.pkl"},
    {"name": "gru.keras", "description": "Modelo GRU", "url": f"{BASE_URL}/gru.keras"},
    {"name": "lstm.keras", "description": "Modelo LSTM", "url": f"{BASE_URL}/lstm.keras"},
    {"name": "simple_rnn.keras", "description": "Modelo SimpleRNN", "url": f"{BASE_URL}/simple_rnn.keras"}
]

st.title("📊 Datasets para los modelos de Machine Learning")
st.markdown("En esta sección puedes descargar los datasets que se utilizaron para entrenar los modelos de Machine Learning.")

tab1, = st.tabs(["Navegador de Archivos"])

with tab1:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Datos")
        for file in files[:4]:
            with st.expander(file["name"]):
                st.write(file["description"])
                st.markdown(f"[Descargar {file['name']}]({file['url']})")

    with col2:
        st.subheader("Datos Escalados")
        for file in files[4:8]:
            with st.expander(file["name"]):
                st.write(file["description"])
                st.markdown(f"[Descargar {file['name']}]({file['url']})")

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Modelos")
        for file in files[12:]:
            with st.expander(file["name"]):
                st.write(file["description"])
                st.markdown(f"[Descargar {file['name']}]({file['url']})")

    with col4:
        st.subheader("Scalers")
        for file in files[8:12]:
            with st.expander(file["name"]):
                st.write(file["description"])
                st.markdown(f"[Descargar {file['name']}]({file['url']})")
