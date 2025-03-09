from datetime import datetime, timedelta
import streamlit as st
from helpers.lookups import elements


def date_range_filter(page: str):

    earliest = api.get_earliest_historical_date()
    latest = api.get_latest_historical_date()

    earliest = datetime.fromisoformat(earliest)
    latest = datetime.fromisoformat(latest)

    default_ini = (latest - timedelta(weeks=2)).isoformat()  
    default_fin = latest.isoformat()

    earliest = earliest.strftime("%Y-%m-%d")
    latest = latest.strftime("%Y-%m-%d")

    fecha_ini = str(st.date_input(label="Fecha inicio", value=default_ini, min_value=earliest, max_value=latest, key=f"fecha_ini_{page}"))
    fecha_fin = str(st.date_input(label="Fecha fin", value=default_fin, min_value=fecha_ini, max_value=latest, key=f"fecha_fin_{page}"))

    return fecha_ini, fecha_fin


def element_filter(selection_mode: str = "single"):

    container = st.container()
    with container:
        selection = st.pills(
            "Elementos",
            options=elements,
            selection_mode=selection_mode,
            label_visibility="collapsed",
            default=elements[0]
        )

    return selection
