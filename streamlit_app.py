import streamlit as st
import pandas as pd
import numpy as np
from thefuzz import process
import matplotlib.pyplot as plt
import datetime as dt

# Header 
st.title('Hope Foundation Data by Stefan')

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


# Load the data into the dataframe and pray it works
@st.cache_data
def import_and_clean(sheet_name: int=0) -> pd.DataFrame:
    url = ("https://github.com/StefVarg1/Semester-Project/raw/refs/heads/main/UNO%20Service%20Learning%20Data%20Sheet%20De-Identified%20Version.xlsx")
    df = pd.read_excel((url), sheet_name=sheet_name)
    st.write("✅ Data is ready to view!")

# Clean the data to have the inconsistent values figured out with thefuzz matching closest option!
# Make values for categories consistent with useful actual values

    if 'Request Status' in df.columns:
        df['Request Status'] = fuzzy_map(df['Request Status'], ['pending', 'approved', 'denied', 'completed'])

    if 'Application Signed?' in df.columns:
        df['Application Signed?'] = fuzzy_map(df['Application Status?'],['n/a', 'no', 'yes'], default='n/a')
    
    # States are so bad in this column, why are so many missing?
    patient_state = {"Nebraska": "NE", "Florida": "FL", "Iowa": "IA", "Kansas": "KS", "Missouri": "MO", "South Dakota": "SD", "Wyoming": "WY", "Colorado": "CO", "Minnesota": "MN"}
    if 'Pt State' in df.columns:
        def map_state(AA):
            if pd.isna(AA) or AA.lower().strip() == 'nan':
                return AA
            match = process.extractOne(AA, list(patient_state))
            return patient_state.get(match[0], AA) if match else AA
        df['Pt State'] = df['Pt State'].astype(str).apply(map_state)

    if 'Marital Status' in df.columns:
        df['Marital Status'] = fuzzy_map(df['Marital Status'], ['Married', 'Divorced', 'Single', 'Widowed','Separated', 'Domestic Partnership'])

    if 'Gender' in df.columns:
        df['Gender'] = fuzzy_map(df['Gender'], ['Female', 'Decline to Answer', 'Male', 'Nonbinary', 'Other', 'Transgender'])

    if 'Race' in df:
        df['Race'] = fuzzy_map(df['Race'], ['American Indian or Alaska Native', 'Asian', 'Black or African American', 'Middle Eastern or North African', 'Native Hawaiian or Pacific Islander', 'White', 'Decline to Answer', 'Other', 'Two or More'], lower=False)

    if 'Insurance Type' in df.columns:
        df['Insurance Type'] = fuzzy_map(df['Insurance Type'], ['Medicare', 'Medicaid', 'Medicare & Medicaid', 'Medicare & Private', 'Medicare & Other', 'Military' 'Uninsured', 'Private'])

    if 'Type of Assistance (CLASS)' in df:
        assistance_type = ['Car Payment', 'Housing', 'Medical Supplies/Prescription Co-pay(s)', 'Phone/Internet', 'Food/Groceries', 'Gas', 'Other', 'Hotel',  'Utilities', 'Multiple']
        df['Type of Assistance (CLASS)'] = fuzzy_map(df['Type of Assistance (CLASS)'], assistance_type, lower=False)

    if 'Payment Submitted?' in df.columns:
        df['Payment Submitted?'] = pd.to_dt(df['Payment Submitted?'], errors='coerce')
    if 'Grant Req Date' in df.columns:
        df['Grant Req Date'] = pd.to_dt(df['Grant Req Date'], errors='coerce')
        df['Year'] = df['Grant Req Date'].dt.year
    
    return df

# Website functions and layout
df = import_and_clean()

if df is not None:
    st.subheader("Clean Data Preview (I hope)")
    st.write(df.columns)
    st.dataframe(df.head(), use_container_width = True)

