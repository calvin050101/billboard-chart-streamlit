import streamlit as st
import pandas as pd
import datetime
from util import get_chart_data
# Import visualization functions from the new file
from viz import plot_peak_vs_weeks, plot_position_change_histogram 

MIN_DATE = datetime.date(1958, 8, 4) # First Billboard Hot 100 chart date
TODAY = datetime.date.today()

@st.cache_data(ttl=3600) # Cache data for 1 hour
def get_hot_100_chart_dataframe(date_str):
    """
    Returns a pandas DataFrame of the Billboard Hot 100 chart for a given date (YYYY-MM-DD).
    Caches the result to avoid redundant API calls.
    """
    try:
        data = get_chart_data(date_str)
        df = pd.DataFrame(data)
        
        # --- ROBUST INITIAL DATA CLEANING ---
        # Ensure all core ranking/week columns are numeric with NaNs for errors
        for col in ["Rank", "Peak Position", "Total Weeks", "Last Week"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        # ------------------------------------
        
        return df
    except Exception as e:
        st.error(f"Could not retrieve chart for {date_str}. Please try a different date. Error: {e}")
        return pd.DataFrame()


def show_section(title, df):
    if not df.empty:
        with st.expander(f"# {title} ({len(df)})"):
            # Prepare DataFrame for display
            display_df = df.copy()
            for col in ["Rank", "Peak Position", "Total Weeks", "Last Week"]:
                if col in display_df.columns:
                    # Convert to nullable integer type for cleaner display (e.g., 1 instead of 1.0)
                    display_df[col] = display_df[col].astype("Int64", errors='ignore')
            
            # FIX: Removed width="stretch" which was causing the TypeError.
            st.dataframe(display_df.reset_index(drop=True)) 


# --- Streamlit UI ---
st.set_page_config(page_title="🎵 Billboard Hot 100 Viewer", layout="centered")

st.title("🎵 Billboard Hot 100 Chart Viewer")
st.markdown("Enter a date to view the Billboard Hot 100 chart for that week.")

selected_date = st.date_input("Select a date", value=TODAY, min_value=MIN_DATE, max_value=TODAY)

def displayData(df, df_last_week):
    
    # --- VISUALIZATIONS SECTION ---
    st.header("📊 Chart Analysis")
    
    # 1. Scatter Plot: Peak Position vs. Total Weeks
    plot_peak_vs_weeks(df)
    st.divider()

    # 2. Histogram: Distribution of Position Changes
    plot_position_change_histogram(df)
    st.divider()
    
    # --- CHART DATA SECTIONS ---
    
    # Find dropouts
    dropouts = df_last_week.loc[
        ~df_last_week["Title"].isin(df["Title"]), ["Rank", "Title", "Artists"]
    ]

    show_section("🏆 Top 100", df.dropna(subset=['Rank'])) 

    # Show Re-peaks and Peakers
    peakers = df.loc[
        (df["Rank"] == df["Peak Position"]) & ~(df["Change"].isin(["=", "NEW"])), :
    ].dropna(subset=['Rank', 'Peak Position'])
    show_section("⛰️ Peakers (New Peak or Re-Peak)", peakers)

    # Gainers: +10 or more
    gainers_data = df.copy()
    gainers_data["Change Int"] = pd.to_numeric(gainers_data["Change"], errors="coerce")
    big_gainers = gainers_data[gainers_data["Change Int"] >= 10].drop(columns="Change Int")
    show_section("📈 Gainers (10+ Spots Up)", big_gainers)

    # Losers: -10 or more
    losers_data = df.copy()
    losers_data["Change Int"] = pd.to_numeric(losers_data["Change"], errors="coerce")
    big_losers = losers_data[losers_data["Change Int"] <= -10].drop(columns="Change Int")
    show_section("📉 Losers (10+ Spots Down)", big_losers)

    # Re-entries
    re_entries = df[df["Change"] == "RE"].drop(columns=["Change", "Last Week"], errors='ignore')
    show_section("🔁 Re-Entries This Week", re_entries)

    # New entries
    new_entries = df[df["Change"] == "NEW"].drop(
        columns=["Change", "Last Week", "Peak Position", "Total Weeks"], errors='ignore'
    )
    show_section("🆕 New Entries This Week", new_entries)

    # Dropouts: Songs that were in last week's chart but not this week's
    dropouts = df_last_week[~df_last_week["Title"].isin(df["Title"])][["Rank", "Title", "Artists"]]
    show_section("🚪 Dropouts (Songs that left the chart)", dropouts.dropna(subset=['Rank']))


if st.button("Get Chart"):
    date_str = selected_date.strftime("%Y-%m-%d")
    with st.spinner(f"Fetching chart for {date_str}..."):
        try:
            df = get_hot_100_chart_dataframe(date_str)
            
            last_week_date = selected_date - datetime.timedelta(days=7)
            df_last_week = get_hot_100_chart_dataframe(last_week_date.strftime("%Y-%m-%d"))

            displayData(df, df_last_week)
        except Exception as e:
            st.error(f"Error fetching chart: {e}")