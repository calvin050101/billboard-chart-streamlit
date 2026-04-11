import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Table Data")

# Helper functions (copied/adapted from main.py)
NUMERIC_COLS = ["Rank", "Peak Position", "Total Weeks", "Last Week"]

def prepare_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.copy()
    for col in NUMERIC_COLS:
        if col in display_df.columns:
            display_df[col] = display_df[col].astype("Int64", errors='ignore')
    return display_df

def show_section(title: str, df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty:
        with st.expander(f"## {title} ({len(df)})"):
            display_df = prepare_dataframe_for_display(df)
            st.dataframe(display_df.reset_index(drop=True), use_container_width=True, 
                         hide_index=True)

def filter_and_show_categories(df: pd.DataFrame, df_last_week: pd.DataFrame):
    df_norm = df.drop(columns="Artists List")
    
    sheets = {}
    
    # --- TOP 100 ---
    top_100 = df_norm.dropna(subset=['Rank'])
    show_section("🏆 Top 100", top_100)
    sheets["Top 100"] = top_100

    # --- PEAKERS ---
    peakers = df_norm.loc[
        (df["Rank"] == df["Peak Position"]) & ~(df["Change"].isin(["=", "NEW"])), :
    ].dropna(subset=['Rank', 'Peak Position'])
    show_section("⛰️ Peakers (New Peak or Re-Peak)", peakers)
    if peakers.empty:
        st.info("No peakers this week.")
    else:
        sheets["Peakers"] = peakers
    
    # --- TOP ARTISTS ---
    artist_count = (
        df.explode('Artists List')
        .groupby('Artists List')
        .agg(
            No_Songs=('Rank', 'count'),
            Best_Rank=('Rank', 'min'),           # Highest chart position
            Median_Rank=('Rank', 'median'),
        )
        .reset_index()
        .rename(columns={
            'Artists List': 'Artist', 'No_Songs': 'No. Songs', 
            'Median_Rank': 'Median Rank', 'Best_Rank': 'Best Rank'
        })
        .sort_values(['No. Songs', 'Best Rank', 'Median Rank'], 
                   ascending=[False, True, True])
    )
    top_artists = artist_count[
        (artist_count['No. Songs'] > 1) &
        (artist_count['Artist'].str.len() > 1)
    ]
    show_section("🎤 Top Artists", top_artists)
    sheets["Top Artists"] = top_artists

    # --- GAINERS & LOSERS ---
    change_data = df_norm.copy()
    change_data["Change Int"] = pd.to_numeric(change_data["Change"], errors="coerce")

    big_gainers = change_data[change_data["Change Int"] >= 10].drop(columns="Change Int")
    if big_gainers.empty:
        st.info("No big gainers this week.")
    else:
        show_section("📈 Gainers (10+ Spots Up)", big_gainers)
        sheets["Gainers"] = big_gainers

    big_losers = change_data[change_data["Change Int"] <= -10].drop(columns="Change Int")
    if big_losers.empty:
        st.info("No big losers this week.")
    else:
        show_section("📉 Losers (10+ Spots Down)", big_losers)
        sheets["Losers"] = big_losers

    # --- RE-ENTRIES ---
    re_entries = df_norm[df["Change"] == "RE"].drop(columns=["Change", "Last Week"], errors='ignore')
    show_section("🔁 Re-Entries This Week", re_entries)
    if re_entries.empty:
        st.info("No re-entries this week.")
    else:   
        sheets["Re-Entries"] = re_entries

    # --- NEW ENTRIES ---
    new_entries = df_norm[df["Change"] == "NEW"].drop(
        columns=["Change", "Last Week", "Peak Position", "Total Weeks"], errors='ignore'
    )
    if new_entries.empty:
        st.info("No new entries this week.")
    else:
        show_section("🆕 New Entries This Week", new_entries)
        sheets["New Entries"] = new_entries

    # --- DROPOUTS ---
    dropouts = df_last_week[~df_last_week["Title"].isin(df["Title"])]\
        [["Rank", "Title", "Artists", "Peak Position", "Total Weeks"]]
    dropouts = dropouts.dropna(subset=['Rank'])
    if dropouts.empty:
        st.info("No dropouts this week.")
    else:
        show_section("🚪 Dropouts", dropouts)
        sheets["Dropouts"] = dropouts
    
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, data in sheets.items():
            data.to_excel(writer, sheet_name=sheet_name[:31], index=False)  
            # Excel sheet names max length = 31

    output.seek(0)
    
    st.download_button(
        label="📥 Download as Excel",
        data=output,
        file_name=f"chart_summary_{st.session_state.chart_date}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


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