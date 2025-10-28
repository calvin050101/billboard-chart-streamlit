import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from util.chart_util import get_chart_data

# ==============================================================================
# 1. CONSTANTS
# ==============================================================================

MIN_DATE = date(1958, 8, 4)
TODAY = date.today()
NUMERIC_COLS = ["Rank", "Peak Position", "Total Weeks", "Last Week"]

# ==============================================================================
# 2. UTILITIES
# ==============================================================================

def get_saturday_of_week(date_input: date) -> str:
    """
    Given a date (datetime.date), return the Saturday of the same week (as 'YYYY-MM-DD').
    The week is defined as Sunday (start) to Saturday (end).
    """
    weekday = (date_input.weekday() + 1) % 7  # Sunday=0, Monday=1, ..., Saturday=6
    saturday = date_input + timedelta(days=(6 - weekday))
    return saturday.strftime("%Y-%m-%d")


def get_effective_chart_date(selected_date: date) -> str:
    """
    Determines the correct chart date:
    - If selected_date is in the current week -> use today's date
    - else -> use the Saturday date of the selected week
    """
    input_saturday = datetime.strptime(get_saturday_of_week(selected_date), "%Y-%m-%d")
    current_saturday = datetime.strptime(get_saturday_of_week(TODAY), "%Y-%m-%d")

    return selected_date if input_saturday == current_saturday else input_saturday.strftime("%Y-%m-%d")


@st.cache_data(ttl=600)
def get_hot_100_chart_dataframe(date_str: str) -> pd.DataFrame:
    """
    Returns a pandas DataFrame of the Billboard Hot 100 chart for a given date.
    Performs robust type conversion on numeric columns.
    """
    try:
        data = get_chart_data(date_str)
        df = pd.DataFrame(data)

        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    except Exception as e:
        st.error(f"Could not retrieve chart for {date_str}. Please try a different date.\n\nError: {e}")
        return pd.DataFrame()

# ==============================================================================
# 3. STREAMLIT UI
# ==============================================================================

st.set_page_config(page_title="🎵 Billboard Hot 100 Viewer", layout="centered")

st.title("🎵 Billboard Hot 100 Chart Viewer")
st.markdown("### 🗓️ Select a date and click **Get Chart** to load the Billboard Hot 100 data across all pages.")

st.session_state.setdefault("df", pd.DataFrame())
st.session_state.setdefault("df_last_week", pd.DataFrame())
st.session_state.setdefault("chart_date", TODAY.strftime("%Y-%m-%d"))

selected_date = st.date_input(
    "Select a date",
    value=TODAY,
    min_value=MIN_DATE,
    max_value=TODAY
)

if st.button("Get Chart"):
    date_str = get_effective_chart_date(selected_date)

    with st.spinner(f"Fetching Billboard Hot 100 chart for **{date_str}**..."):
        try:
            df = get_hot_100_chart_dataframe(date_str)

            last_week_date = selected_date - timedelta(days=7)
            df_last_week = get_hot_100_chart_dataframe(last_week_date.strftime("%Y-%m-%d"))

            if not df.empty:
                st.session_state.df = df
                st.session_state.df_last_week = df_last_week
                st.session_state.chart_date = date_str
                st.success(f"✅ Chart data for **{date_str}** successfully loaded!")
            else:
                st.warning("The selected chart data could not be retrieved or is empty.")

        except Exception as e:
            st.error(f"An unexpected error occurred: \n\n{e}")


# Display success message if data is loaded
if not st.session_state.df.empty:
    st.info(f"Data for **{st.session_state.chart_date}** is ready. Navigate to the pages on the left sidebar.")