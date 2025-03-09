import streamlit as st
from helpers.lookups import elements


def element_tabs():

    tabs = [element.capitalize() for element in elements]

    if "selected_element" not in st.session_state:
        st.session_state.selected_element = tabs[0].lower()

    cols = st.columns(len(tabs))

    for i, tab in enumerate(cols):
        def click_tab(tab_name=tabs[i]):
            st.session_state.selected_element = tab_name.lower()

        if tabs[i].lower() == st.session_state.selected_element:
            tab.button(tabs[i], key=f"tab_{i}", on_click=click_tab, use_container_width=True)
        else:
            tab.button(tabs[i], key=f"tab_{i}", on_click=click_tab, use_container_width=True)
