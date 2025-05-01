import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# -- CONFIGURATION --

st.title('Hope Foundation Data by Stefan')

@st.cache_data
def load_data():
    """Load and cache the service data CSV."""
    df = pd.read_csv('UNO Service Learning Data Sheet De-Identified Version.csv', parse_dates=["request_received", "support_sent"])
    # Clean or rename columns here if needed
    return df


DATE_COLUMN = 'Grant Req Date'
DATA_URL = ('https://github.com/StefVarg1/Semester-Project/blob/main/UNO%20Service%20Learning%20Data%20Sheet%20De-Identified%20Version.csv'
         'UNO Service Learning Data Sheet De-Identified Version.csv')

def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


def main():
    st.sidebar.title("Navigation")
    pages = {
        "Ready for Review": page_ready_for_review,
        "Support by Demographics": page_support_by_demographics,
        "Processing Time": page_processing_time,
        "Unspent Grants": page_unspent_grants,
        "Annual Summary": page_summary,
    }
    choice = st.sidebar.radio("Go to", list(pages.keys()))
    df = load_data()
    pages[choice](df)

if __name__ == "__main__":
    main()


