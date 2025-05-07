import streamlit as st
import pandas as pd
import numpy as np
from thefuzz import process
import matplotlib.pyplot as plt
import plotly.express as px
import datetime as dt

# Functions to help with figuring out the inconsistent data

def fuzzy_map(series: pd.Series, options: list[str], default=np.nan, lower: bool = True) -> pd.Series:
    """
    Fuzzy-match every value in the 'series' to the closest possible 'options'.
    Should return the matched option or 'default' if input is null, nan or can't match.
    """
    opts = [opt.lower() if lower else opt for opt in options]
    def _match(excel_value):
        if pd.isna(excel_value):
            return default
        text = excel_value.lower() if lower else str(excel_value)
        match, score = process.extractOne(text, opts)
        return match if score >= 70 else default
    return series.astype(str).apply(_match)


# Load the data into the dataframe and pray it works
@st.cache_data
def import_and_clean(sheet_name: int=0) -> pd.DataFrame:
    url = ("https://github.com/StefVarg1/Semester-Project/raw/refs/heads/main/UNO%20Service%20Learning%20Data%20Sheet%20De-Identified%20Version.xlsx")
    df = pd.read_excel((url), sheet_name=sheet_name)
    st.write("✅Ready for Review!")

# Clean the data to have the inconsistent values figured out with thefuzz matching closest option!
# Make values for categories consistent with useful actual values

    if 'Request Status' in df.columns:
        df['Request Status'] = fuzzy_map(df['Request Status'], ['Pending', 'Approved', 'Denied', 'Completed'])

    if 'Application Signed?' in df.columns:
        df['Application Signed?'] = fuzzy_map(df['Application Signed?'],['N/A', 'NO', 'YES'], default='Unknown')
    
    # States are so bad in this column, why are so many missing?
    pt_state = {"Nebraska": "NE", "Florida": "FL", "Iowa": "IA", "Kansas": "KS", "Missouri": "MO", "South Dakota": "SD", "Wyoming": "WY", "Colorado": "CO", "Minnesota": "MN"}
    if 'Pt State' in df.columns:
        def map_state(x):
            if pd.isna(x) or x.lower().strip() == 'nan':
                return x
            match = process.extractOne(x, list(pt_state))
            return pt_state.get(match[0], x) if match else x
        df['Pt State'] = df['Pt State'].astype(str).apply(map_state)

    if 'Marital Status' in df.columns:
        df['Marital Status'] = fuzzy_map(df['Marital Status'], ['Married', 'Divorced', 'Single', 'Widowed','Separated', 'Domestic Partnership'])

    if 'Gender' in df.columns:
        df['Gender'] = fuzzy_map(df['Gender'], ['Female', 'Decline to Answer', 'Male', 'Nonbinary', 'Other', 'Transgender'])

    if 'Race' in df:
        df['Race'] = fuzzy_map(df['Race'], ['American Indian or Alaska Native', 'Asian', 'Black or African American', 'Middle Eastern or North African', 'Native Hawaiian or Pacific Islander', 'White', 'Decline to Answer', 'Other', 'Two or More'], lower=False)

    if 'Insurance Type' in df.columns:
        df['Insurance Type'] = fuzzy_map(df['Insurance Type'], ['Medicare', 'Medicaid', 'Medicare & Medicaid', 'Medicare & Private', 'Medicare & Other', 'Military', 'Uninsured', 'Private'])

    if 'Type of Assistance (CLASS)' in df:
        assistance_type = ['Car Payment', 'Housing', 'Medical Supplies/Prescription Co-pay(s)', 'Phone/Internet', 'Food/Groceries', 'Gas', 'Other', 'Hotel',  'Utilities', 'Multiple']
        df['Type of Assistance (CLASS)'] = fuzzy_map(df['Type of Assistance (CLASS)'], assistance_type, lower=False)

    if 'Payment Submitted?' in df.columns:
        df['Payment Submitted?'] = pd.to_datetime(df['Payment Submitted?'], errors='coerce')

    if 'Grant Req Date' in df.columns:
        df['Grant Req Date'] = pd.to_datetime(df['Grant Req Date'], errors='coerce')
        df['Year'] = df['Grant Req Date'].dt.year
    
    if 'Total Household Gross Monthly Income' in df:
        df['Total Household Gross Monthly Income'] = pd.to_numeric(df['Total Household Gross Monthly Income'], errors='coerce')
        df['Total Household Gross Annual Income'] = ['Total Household Gross Monthly Income'] * 12
        def income_level(x):
            if pd.isna(x):
                return pd.NA
            if x <= 15650:
                return "Below Poverty Threshold"
            if 15650 < x <= 19562.5:
                return "Between Thershold & 125% Multiple"
            if 19562.5 < x <= 23475:
                return "Between 125% & 150% Multiple"
            if 23475 < x <= 28925.5:
                return "Between 150% & 185% Multiple"
            if 28925.5 < x <= 70000:
                return "Between 185% Multiple and Median Household Income"
            if 70000 < x:
                return "Above Median"
            df['Household Gross Annual Income Level'] = df['Total Household Gross Annual Income'].apply(income_level)
            
    return df

# Website functions and layout
st.title('Hope Foundation Data by Stefan')
df = import_and_clean()

selected = st.sidebar.selectbox("Pages", ["Filter Table", "Payment Based on Demographics", "Request to Response Time", "Grant Amounts by Categories"])

if selected == "Filter Table":
    st.subheader(selected)
    columns = df.columns.tolist()
    selected_column = st.selectbox("Select column to filter by", columns)
    unique_values = df[selected_column].unique()
    selected_value = st.selectbox("Select value", unique_values)
    filtered_df = df[df[selected_column] == selected_value]
    st.write(filtered_df)

else:
    selected == "Payment Based on Demographics"
    st.subheader(selected)

