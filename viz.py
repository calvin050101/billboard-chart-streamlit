import streamlit as st
import altair as alt

from util.viz_util import (
    LONGEVITY_ORDER,
    get_peak_vs_weeks_data,
    get_position_change_distribution_data,
    get_week_distribution_data
)

# Visualization Functions

def plot_total_weeks_distribution(df):
    """
    Creates and displays a bar chart of songs grouped by their longevity categories (Total Weeks).
    Uses the efficient categorize_longevity_pythonic function.
    """
    st.subheader("Chart Longevity Distribution")

    chart_data = get_week_distribution_data(df)
    
    if chart_data.empty:
        st.info("No data available to generate the Longevity Distribution chart.")
        return

    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('Longevity Category:N', sort=LONGEVITY_ORDER, 
                title='Total Weeks Category', axis=alt.Axis(labelAngle=0)), 
        y=alt.Y('Count:Q', title='Number of Songs'),
        tooltip=['Longevity Category', 'Count'],
        color=alt.Color('Longevity Category:N', legend=None)
    ).properties(
        width='container',
        height=400
    )

    text = bar_chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        text='Count:Q',
        color=alt.value('black')
    )
    
    st.altair_chart(bar_chart + text, use_container_width=True)


def plot_peak_vs_weeks(df):
    """
    Creates and displays a scatter plot of Peak Position vs. Total Weeks,
    with colors classified by position changes.
    """
    CHANGE_COLOR_SCALE = alt.Scale(
        domain=["Up", "Down", "Same", "Return", "New", "Unknown"],
        range=["#2ca02c", "#d62728", "#1f77b4", "#ff7f0e", "#9467bd", "#8c8c8c"]
    )
    
    st.subheader("Peak Position vs. Total Weeks on Chart")
    
    plot_data = get_peak_vs_weeks_data(df)
    
    if plot_data.empty:
        st.info("No data available to generate the Peak Position vs. Total Weeks plot.")
        return

    scatter_chart = alt.Chart(plot_data).mark_circle(size=80).encode(
        x=alt.X('Total Weeks:Q', title='Total Weeks on Chart'),
        y=alt.Y('Peak Position:Q', scale=alt.Scale(reverse=True), 
                axis=alt.Axis(tickMinStep=1), title='Peak Position'),
        tooltip=['Title', 'Artists', 'Total Weeks', 'Peak Position', 'Rank', 
                 'Change', 'Change Category'],
        color=alt.Color('Change Category:N', scale=CHANGE_COLOR_SCALE, title='Position Change'),
        order=alt.Order('Change Category', sort='descending')
    ).properties(
        width='container',
        height=400
    ).interactive() 
    
    st.altair_chart(scatter_chart, use_container_width=True)


def plot_position_change_histogram(df):
    """
    Creates and displays a histogram of position changes, excluding NEW, RE, and =.
    """
    st.subheader("Distribution of Position Changes")
    
    change_data = get_position_change_distribution_data(df)

    if change_data.empty:
        st.info(
            "No data available to generate the Position Changes histogram "+
            "(all songs were NEW, RE, or =)."
        )
        return
    
    BIN_SIZE = 5
    
    hist_chart = alt.Chart(change_data).mark_bar().encode(
        x=alt.X(
            'Position Change Value:Q', 
            bin=alt.Bin(step=BIN_SIZE), 
            title='Position Change (Spots)'
        ),
        y=alt.Y('count():Q', title='Number of Songs'),
        tooltip=[
            alt.Tooltip(
                'Position Change Value:Q', 
                bin=alt.Bin(step=BIN_SIZE), 
                title='Position Change Range'
            ), 
            'count():Q'
        ],
        color=alt.value("teal")
    ).properties(
        width='container',
        height=400
    )
    
    text = hist_chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-4
    ).encode(
        text=alt.Text('count():Q'),
        tooltip=[]
    )

    st.altair_chart(hist_chart + text, use_container_width=True)