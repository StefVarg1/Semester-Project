import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# -- CONFIGURATION --

st.title('Hope Foundation Data by Stefan')

DATE_COLUMN = 'Grant Req Date'
DATA_URL = ('https://github.com/StefVarg1/Semester-Project/blob/main/UNO%20Service%20Learning%20Data%20Sheet%20De-Identified%20Version.csv'
         'UNO Service Learning Data Sheet De-Identified Version.csv')

def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(1000)
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')


