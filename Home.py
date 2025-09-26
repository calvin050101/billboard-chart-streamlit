import streamlit as st
import pandas as pd
import datetime
from util.chart_util import get_chart_data

# ==============================================================================
# 1. CONSTANTS & DATA CACHING
# ==============================================================================

# Chart date constants
MIN_DATE = datetime.date(1958, 8, 4)
TODAY = datetime.date.today()
NUMERIC_COLS = ["Rank", "Peak Position", "Total Weeks", "Last Week"]

@st.cache_data(ttl=3600)
def get_hot_100_chart_dataframe(date_str):
    """
    Returns a pandas DataFrame of the Billboard Hot 100 chart for a given date.
    Performs robust type conversion on key columns.
    """
    try:
        data = get_chart_data(date_str)
        df = pd.DataFrame(data)

        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Could not retrieve chart for {date_str}. Please try a different date. Error: {e}")
        return pd.DataFrame()


# ==============================================================================
# 2. STREAMLIT UI SETUP & DATA FETCHING
# ==============================================================================

st.set_page_config(page_title="🎵 Billboard Hot 100 Viewer", layout="centered")

st.title("🎵 Billboard Hot 100 Chart Viewer")
st.markdown("### 🗓️ Select a date and click 'Get Chart' to load the data across all pages.")

# Initialize session state for data storage if it doesn't exist
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'df_last_week' not in st.session_state:
    st.session_state.df_last_week = pd.DataFrame()
if 'chart_date' not in st.session_state:
    st.session_state.chart_date = TODAY.strftime("%Y-%m-%d")


selected_date = st.date_input(
    "Select a date",
    value=TODAY,
    min_value=MIN_DATE,
    max_value=TODAY
)

if st.button("Get Chart"):
    date_str = selected_date.strftime("%Y-%m-%d")

    with st.spinner(f"Fetching chart for {date_str}..."):
        try:
            # Fetch current and last week's data
            df = get_hot_100_chart_dataframe(date_str)
            last_week_date = selected_date - datetime.timedelta(days=7)
            df_last_week = get_hot_100_chart_dataframe(last_week_date.strftime("%Y-%m-%d"))

            if not df.empty:
                # Store data in session state for other pages to access
                st.session_state.df = df
                st.session_state.df_last_week = df_last_week
                st.session_state.chart_date = date_str
                st.success(f"Chart data for {date_str} successfully loaded!")
            else:
                st.warning("The selected chart data could not be retrieved or is empty.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Display success message if data is loaded
if not st.session_state.df.empty:
    st.info(f"Data for **{st.session_state.chart_date}** is ready. Navigate to the pages on the left sidebar.")