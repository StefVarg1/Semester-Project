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

    if 'Pt City' in df.columns:
        df['Pt City'] = fuzzy_map(df['Pt City'], ['Adams', 'Ansely', 'Arcadia', 'Ashland', 'Auburn', 'Beatrice', 'Bennington', 'Bennet', 'Bison', 'Blue Hill', 'Blue Rapids', 'Bridgeport', 'Broken Bow', 'Campbell', 'Cairo', 'Central City', 'Chapman', 'Chaule', 'Columbus', 'Concord', 'Cozad', 'Crab Orchard', 'Crookston', 'Council Bluffs', 'Davenport', 'David City', 'Doniphan', 'Dwight', 'Eagle', 'Earling', 'Elkhorn', 'Elwood', 'Exeter', 'Fairbury', 'Fairfield', 'Fairmont', 'Falls City', 'Friend', 'Fremont', 'Fullerton', 'Genoa', 'Gilead', 'Glenwood', 'Gretna', 'Hallam', 'Harvard', 'Hastings', 'Hershey', 'Holdrege', 'Humboldt', 'Imperial', 'Inavale', 'Inland', 'Kearney', 'Kenesaw', 'La Vista', 'Lexington', 'Liberty', 'Lincoln', 'LInwood', 'Loomis', 'Maskell', 'McCook', 'Milford', 'Monroe', 'Nebraska City', 'Nelson', 'North Platte', 'Oakland', 'Odell', 'Ogallala', 'Omaha', 'Onconto', 'Ord', 'Oshkosh', 'Overton', 'Palm Coast', 'Palmyra', 'Panama', 'Papillion', 'Pawnee City', 'Persia', 'Platte Center', 'Pleasanton', 'Polic', 'Prague', 'Raymond', 'Red Cloud', 'Rockville', 'Rosalie', 'Roseland', 'St Paul', 'Scribner', 'Sioux City', 'Stromsburg', 'Superior', 'Swanton', 'Syracuse', 'Taylor', 'Tekamah', 'Tecumseh', 'Talmage', 'Valparaiso', 'Valley', 'Virginia', 'Walthill', 'Waverly', 'Wahoo', 'Wilber', 'Wymore', 'York']
        , lower=False)

    if 'Gender' in df.columns:
        df['Gender'] = fuzzy_map(df['Gender'], ['Female', 'Decline to Answer', 'Male', 'Nonbinary', 'Other', 'Transgender'])

    if 'Sexual Orientation' in df.columns:
        df['Sexual Orientation'] = fuzzy_map(df['Sexual Orientation'], ['Straight', 'Decline', 'Bisexual', 'Gay or Lesbian', 'Heterosexual'])

    if 'Race' in df:
        df['Race'] = fuzzy_map(df['Race'], ['American Indian or Alaska Native', 'Asian', 'Black or African American', 'Middle Eastern or North African', 'Native Hawaiian or Pacific Islander', 'White', 'Decline to Answer', 'Other', 'Two or More'], lower=False)

    if 'Hispanic/Latino' in df:
        df['Hispanic/Latino'] = fuzzy_map(df['Hispanic/Latino'], ['Hispanic or Latino', 'yes'])
        
    if 'Insurance Type' in df.columns:
        df['Insurance Type'] = fuzzy_map(df['Insurance Type'], ['Medicare', 'Medicaid', 'Medicare & Medicaid', 'Medicare & Private', 'Medicare & Other', 'Military', 'Uninsured', 'Private'])

    if 'Type of Assistance (CLASS)' in df:
        assistance_type = ['Car Payment', 'Housing', 'Medical Supplies/Prescription Co-pay(s)', 'Phone/Internet', 'Food/Groceries', 'Gas', 'Other', 'Hotel',  'Utilities', 'Multiple']
        df['Type of Assistance (CLASS)'] = fuzzy_map(df['Type of Assistance (CLASS)'], assistance_type, lower=False)

    if 'Payment Submitted?' in df.columns:
        df['Payment Submitted?'] = pd.to_datetime(df['Payment Submitted?'], format="%m/%d/%Y", errors='coerce')

    if 'DOB' in df.columns:
        df['DOB'] = pd.to_datetime(df['DOB'], format="%m/%d/%Y", errors='coerce')

    if 'Grant Req Date' in df.columns:
        df['Grant Req Date'] = pd.to_datetime(df['Grant Req Date'], format="%m/%d/%Y", errors='coerce')
        df['Year'] = df['Grant Req Date'].dt.year

    if 'Amount' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    if 'Total Household Gross Monthly Income' in df:
        df['Total Household Gross Monthly Income'] = pd.to_numeric(df['Total Household Gross Monthly Income'], errors='coerce')
        df['Total Household Gross Annual Income'] = df['Total Household Gross Monthly Income'] * 12
    def income_level(x):
        if pd.isna(x):
            return pd.NA
        if x <= 15650:
            return "Below Poverty Threshold"
        if 15650 < x <= 19562.5:
            return "Between Threshold & 125% Multiple"
        if 19562.5 < x <= 23475:
            return "Between 125% & 150% Multiple"
        if 23475 < x <= 28925.5:
            return "Between 150% & 185% Multiple"
        if 28925.5 < x <= 70000:
            return "Between 185% & Median Income"
        return "Above Median"

    df['Household Gross Annual Income Level'] = df['Total Household Gross Annual Income'].apply(income_level)
    
    return df

# Website functions and layout
st.title('Hope Foundation Data by Stefan')
df = import_and_clean()

selected = st.sidebar.selectbox("Pages", ["Filter Table", "Support Based on Demographics", "Request to Response Time", "Grant Amounts by Categories", "Unspent Grants Summary", "Impact Summary for Stakeholders"])

if selected == "Filter Table":
    st.subheader("Filtered Table")
    st.dataframe(df)

elif selected == "Support Based on Demographics":
    st.subheader("Support by Demographics")
    st.write('Support by Gender and Insurance Type')

    if {'Amount', 'Gender', 'Insurance Type'}.issubset(df.columns):
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        filtered = df.dropna(subset=['Amount', 'Gender', 'Insurance Type'])

        grouped = (filtered.groupby(['Insurance Type', 'Gender'])['Amount'].sum().reset_index())

        fig = px.bar(grouped,
            x='Insurance Type',
            y='Amount',
            color='Gender',
            barmode='group',
            labels={'Amount': 'Total Support Amount ($)'},
            title='Support Amount by Insurance Type and Gender'
        )
        st.plotly_chart(fig, use_container_width=True)
    
        st.write("Support by State")

        grouped_state = (filtered.groupby('Pt State')['Amount'].sum().sort_values(ascending=False).reset_index())
        
        fig2 = px.bar(grouped_state,
            x='Pt State',
            y='Amount',
            labels={'Amount': 'Total Support Amount ($)', 'Pt State': 'Patient State'},
            title='Total Support Amount by Patient State'
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.write("Support by City")

        grouped_city = (filtered.groupby(['Pt City', 'Gender'])['Amount'].sum().sort_values(ascending=False).reset_index())
        
        fig3 = px.bar(grouped_city,
            x='Pt City',
            y='Amount',
            color = 'Gender',
            labels={'Amount': 'Total Support Amount ($)', 'Pt City': 'Patient City'},
            title='Total Support Amount by Patient City'
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.write('Support by Race and Gender')

        grouped_race = (filtered.groupby(['Race', 'Gender'])['Amount'].mean().sort_values(ascending=False).reset_index())
        
        fig4 = px.bar(grouped_race,
            x='Race',
            y='Amount',
            color = 'Gender',
            labels={'Amount': 'Average Support Amount ($)', 'Race': 'Race'},
            title='Average Support Amount by Patient Race'
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.write('Support by Income Level')

        grouped_income = (filtered.groupby(['Household Gross Annual Income Level'])['Amount'].mean().sort_values(ascending=False).reset_index())
        
        fig5 = px.bar(grouped_income,
            x='Household Gross Annual Income Level',
            y='Amount',
            labels={'Amount': 'Average Support Amount ($)', 'Household Gross Annual Income Level': 'Household Gross Annual Income Level'},
            title='Average Support Amount by Patient Income Level'
        )
        st.plotly_chart(fig5, use_container_width=True)

    else:
        st.warning("Missing one or more of the required columns: 'Amount', 'Gender', 'Insurance Type', 'Pt State', 'Pt City', 'Race', 'Household Gross Annual Income Level")

    # Time between request and response time for patients
elif selected == "Request to Response Time":
    st.subheader("Time Between Request and Payment")
    if {'Grant Req Date', 'Payment Submitted?'}.issubset(df.columns):
        df['Days to Response'] = (df['Payment Submitted?'] - df['Grant Req Date']).dt.days
        st.plotly_chart(px.histogram(df, x='Days to Response'))

elif selected == "Unspent Grants Summary":
    st.subheader("Patients Who Did Not Use Full Grant Amount")

    if 'Year' in df.columns and {'Remaining Balance', 'Patient ID#', 'Amount', 'Type of Assistance (CLASS)'}.issubset(df.columns):
        year = st.selectbox("Select Application Year", sorted(df['Year'].dropna().unique()), key="unspent_year")
        df_y = df[df['Year'] == year].copy()

        df_y['Remaining Balance'] = pd.to_numeric(df_y['Remaining Balance'], errors='coerce')
        df_y['Amount'] = pd.to_numeric(df_y['Amount'], errors='coerce')

        # Patients with remaining balances 
        incomplete = df_y[df_y['Remaining Balance'] > 0]
        num_incomplete = incomplete['Patient ID#'].nunique()

        st.write(f"Number of patients who did not use full grant in {year}: {num_incomplete}")

        # Average support amount by assistance type
        if 'Type of Assistance (CLASS)' in df_y.columns:
            avg_by_type = (
                df_y.groupby('Type of Assistance (CLASS)')['Amount']
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )

            st.write("Average Amount Given by Type of Assistance")
            st.dataframe(avg_by_type, use_container_width=True)
            st.plotly_chart(
                px.bar(avg_by_type, x='Type of Assistance (CLASS)', y='Amount',
                       title='Average Support Amount by Assistance Type',
                       labels={'Amount': 'Average Amount ($)'})
            )
    else:
        st.warning("Required columns not found: 'Remaining Balance', 'Amount', 'Type of Assistance (CLASS)', or 'Year'")

elif selected == "Grant Amounts by Categories":
    st.subheader("Grant Amounts by Type of Assistance")
    if 'Type of Assistance (CLASS)' in df and 'Amount' in df:
        grouped = df.groupby('Type of Assistance (CLASS)')['Amount'].sum().reset_index()
        st.plotly_chart(px.bar(grouped, x='Type of Assistance (CLASS)', y='Amount'))

elif selected == "Impact Summary for Stakeholders":
    st.subheader("Impact Summary Report")

    if 'Year' in df.columns and 'Amount' in df.columns and 'Patient ID#' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        most_recent_year = int(df['Year'].dropna().max())
        last_year_data = df[df['Year'] == most_recent_year].copy()

        st.markdown(f"### Summary for {most_recent_year}")

        total_patients = last_year_data['Patient ID#'].nunique()
        total_disbursed = last_year_data['Amount'].sum()
        avg_per_patient = last_year_data.groupby('Patient ID#')['Amount'].sum().mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Patients Served", f"{total_patients}")
        col2.metric("Total Support Distributed", f"${total_disbursed}")
        col3.metric("Average Support per Patient", f"${avg_per_patient}")

        # Support amount distributed by assitance type 
        if 'Type of Assistance (CLASS)' in last_year_data.columns:
            st.markdown("Distribution by Assistance Type")
            type_breakdown = (last_year_data.groupby('Type of Assistance (CLASS)')['Amount'].sum().sort_values(ascending=False).reset_index())

            fig = px.pie(type_breakdown,
                names='Type of Assistance (CLASS)',
                values='Amount',
                title='Support Allocation by Assistance Category'
            )
            st.plotly_chart(fig)

        # Demographic information for the year 
        if {'Gender', 'Insurance Type'}.issubset(last_year_data.columns):
            st.markdown("Demographic information for the year")
            demo_col1, demo_col2 = st.columns(2)

            gender_split = last_year_data['Gender'].value_counts().reset_index()
            gender_split.columns = ['Gender', 'Count']
            demo_col1.plotly_chart(
                px.bar(gender_split, 
                x='Gender', 
                y='Count', 
                title='Patients by Gender')
            )

            insurance_split = last_year_data['Insurance Type'].value_counts().reset_index()
            insurance_split.columns = ['Insurance Type', 'Count']
            demo_col2.plotly_chart(
                px.bar(insurance_split, 
                x='Insurance Type', 
                y='Count', 
                title='Patients by Insurance Type')
            )
    else:
        st.warning("Required columns missing: 'Year', 'Amount', or 'Patient ID#'")