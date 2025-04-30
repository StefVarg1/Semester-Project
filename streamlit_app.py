#Hello World

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Hope Foundation Data",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    return pd.read_csv('UNO Service Learning Data Sheet De-Identified Version.csv')

data = load_data
