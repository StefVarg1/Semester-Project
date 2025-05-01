import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# -- CONFIGURATION --

@st.cache_data
def load_data():
    """Load and cache the service data CSV."""
    df = pd.read_csv('UNO Service Learning Data Sheet De-Identified Version.csv', parse_dates=["request_received", "support_sent"])
    # Clean or rename columns here if needed
    return df


# -- MAIN --

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



