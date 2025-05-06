import streamlit as st
import pandas as pd
import numpy as np
from thefuzz import process



# Functions to help with figuring out the inconsistent data

def fuzzy_map(series: pd.Series, options: list[str], default=np.nan, lower: bool = True) -> pd.Series:
    """
    Fuzzy-match every value in the 'series' to the closest possible 'options'.
    Should return the matched option or 'default' if input is null, nan or can't match.
    """
    opts = [opt.lower() if lower else opt for opt in options]
    def _match(excel_value):
        if pd.isa(excel_value):
            return default
        text = excel_value.lower() if lower else str(excel_value)
        match, score = process.extractOne(text, opts)
        return match if score >= 55 else default
    return series.astype(str).apply(_match)

@st.cache_data
def import_and_clean(sheet_name=0) -> pd.DataFrame:
    # 1) Load
    url = ("https://github.com/StefVarg1/Semester-Project/raw/refs/heads/main/UNO%20Service%20Learning%20Data%20Sheet%20De-Identified%20Version.xlsx")
    df = pd.read_excel((url), sheet_name=sheet_name)
    st.write("✅ Data is ready to view!")

