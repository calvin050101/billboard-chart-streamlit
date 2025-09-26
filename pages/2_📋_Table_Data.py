import streamlit as st
import pandas as pd

st.set_page_config(page_title="Table Data")

# Helper functions (copied/adapted from main.py)
NUMERIC_COLS = ["Rank", "Peak Position", "Total Weeks", "Last Week"]

def prepare_dataframe_for_display(df):
    display_df = df.copy()
    for col in NUMERIC_COLS:
        if col in display_df.columns:
            display_df[col] = display_df[col].astype("Int64", errors='ignore')
    return display_df

def show_section(title, df):
    if not df.empty:
        with st.expander(f"## {title} ({len(df)})"):
            display_df = prepare_dataframe_for_display(df)
            # Use use_container_width=True for better table display on wide screens
            st.dataframe(display_df.reset_index(drop=True), use_container_width=True)


def filter_and_show_categories(df, df_last_week):
    """Groups filtering logic for chart categories (Gainers, Losers, New, etc.)."""

    # --- TOP 100 ---
    show_section("🏆 Top 100", df.dropna(subset=['Rank']))

    # --- PEAKERS ---
    peakers = df.loc[
        (df["Rank"] == df["Peak Position"]) & ~(df["Change"].isin(["=", "NEW"])), :
    ].dropna(subset=['Rank', 'Peak Position'])
    show_section("⛰️ Peakers (New Peak or Re-Peak)", peakers)

    # --- GAINERS & LOSERS ---
    change_data = df.copy()
    change_data["Change Int"] = pd.to_numeric(change_data["Change"], errors="coerce")

    big_gainers = change_data[change_data["Change Int"] >= 10].drop(columns="Change Int")
    show_section("📈 Gainers (10+ Spots Up)", big_gainers)

    big_losers = change_data[change_data["Change Int"] <= -10].drop(columns="Change Int")
    show_section("📉 Losers (10+ Spots Down)", big_losers)

    # --- RE-ENTRIES ---
    re_entries = df[df["Change"] == "RE"].drop(columns=["Change", "Last Week"], errors='ignore')
    show_section("🔁 Re-Entries This Week", re_entries)

    # --- NEW ENTRIES ---
    new_entries = df[df["Change"] == "NEW"].drop(
        columns=["Change", "Last Week", "Peak Position", "Total Weeks"], errors='ignore'
    )
    show_section("🆕 New Entries This Week", new_entries)

    # --- DROPOUTS ---
    dropouts = df_last_week[~df_last_week["Title"].isin(df["Title"])][["Rank", "Title", "Artists"]]
    show_section("🚪 Dropouts (Songs that left the chart)", dropouts.dropna(subset=['Rank']))


# ==============================================================================
# PAGE EXECUTION
# ==============================================================================
st.title("📋 Detailed Chart Data")

# Check if data is available in session state
if st.session_state.df.empty:
    st.error("Please select a date and click 'Get Chart' on the home page.")
else:
    df = st.session_state.df
    df_last_week = st.session_state.df_last_week
    st.markdown(f"### Data for Chart Date: {st.session_state.chart_date}")

    filter_and_show_categories(df, df_last_week)