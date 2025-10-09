import streamlit as st
from viz import (
    plot_peak_vs_weeks,
    plot_position_change_histogram,
    plot_total_weeks_distribution,
)

st.set_page_config(page_title="Charts", layout="wide")

st.title("📊 Chart Visualizations")

# Check if data is available in session state
if st.session_state.df.empty:
    st.error("Please select a date and click 'Get Chart' on the home page.")
else:
    df = st.session_state.df
    df_last_week = st.session_state.df_last_week
    st.markdown(f"### Data for Chart Date: {st.session_state.chart_date}")
    
    plot_total_weeks_distribution(df)
    st.divider()

    plot_peak_vs_weeks(df)
    st.divider()

    plot_position_change_histogram(df)
    st.divider()