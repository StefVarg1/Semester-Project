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

# -- PAGE FUNCTIONS --
def page_ready_for_review(df):
    st.title("Applications Ready for Review")
    df_ready = df[df["status"] == "Ready for Review"]
    signed = st.checkbox("Only signed by committee?", value=False)
    if signed:
        df_ready = df_ready[df_ready["signed_by_committee"] == True]
    st.dataframe(df_ready)


def page_support_by_demographics(df):
    st.title("Support Amounts by Demographics")
    dims = ["location", "gender", "income_bracket", "insurance_type", "age_group"]
    sel = st.multiselect("Select demographics to group by", dims, default=["location"])
    grp = df.groupby(sel)["support_amount"].sum().reset_index()
    st.bar_chart(grp.set_index(sel))


def page_processing_time(df):
    st.title("Processing Time: Request to Support Sent")
    df["processing_days"] = (df["support_sent"] - df["request_received"]).dt.days
    st.histogram(df["processing_days"], bins=30, ylabel="Count")


def page_unspent_grants(df):
    st.title("Unspent Grants & Averages by Assistance Type")
    df["unspent"] = df["grant_amount"] - df["support_amount"]
    current_year = datetime.now().year
    year = st.selectbox("Select application year", df["application_year"].unique(), index=0)
    subset = df[df["application_year"] == year]
    not_full = subset[subset["unspent"] > 0]
    st.write(f"Number of partially used grants in {year}: {len(not_full)}")
    avg_by_type = subset.groupby("assistance_type")["support_amount"].mean()
    st.table(avg_by_type)


def page_summary(df):
    st.title("Annual Impact Summary")
    year = datetime.now().year - 1
    subset = df[df["application_year"] == year]
    st.metric("Total Applications", len(subset))
    st.metric("Total Support Distributed", subset["support_amount"].sum())
    st.metric("Average Support per Case", subset["support_amount"].mean())
    st.write("### Demographic breakdown:")
    st.dataframe(subset.groupby("location")["support_amount"].sum().sort_values(ascending=False))

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



