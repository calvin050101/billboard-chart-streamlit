import streamlit as st
import altair as alt

from util.viz_util import (
    LONGEVITY_ORDER,
    get_peak_vs_weeks_data,
    get_position_change_distribution_data,
    get_top_10_line_chart_data,
    get_week_distribution_data
)

# ==============================================================================
# VISUALIZATION FUNCTIONS
# ==============================================================================

def plot_top_10_line_chart(df, df_last_week):
    """
    Creates and displays a line chart (Lollipop chart style) showing the rank 
    change of current Top 10 songs over the last two weeks, with points only 
    displayed at the Current Rank position.
    """
    st.subheader("Top 10 Rank Change (Previous Week vs. Current Week)")

    # --- Data Creation Call ---
    rank_comparison_long, top_10_titles = get_top_10_line_chart_data(df, df_last_week)

    if not top_10_titles:
        st.info("No songs are currently in the Top 10.")
        return

    # --- Scaling and Encoding ---
    data_max_rank = rank_comparison_long['Rank Value'].max()
    Y_DOMAIN_MAX = data_max_rank + 5
    
    X_AXIS_ORDER = ['Previous Rank', 'Current Rank']
    y_scale = alt.Scale(reverse=True, domain=[0, Y_DOMAIN_MAX])
    color_encoding = alt.Color('Song Details:N', title='Song')

    # 1. Base Chart (Uses ALL data for lines)
    base = alt.Chart(rank_comparison_long).properties(
        width='container',
        height=500,
        title='Rank Change of Current Top 10 Songs (Previous vs. Current Week)'
    )
    
    # 2. Filtered Data for Points (Current Rank only)
    points_data = rank_comparison_long[rank_comparison_long['Week Type'] == 'Current Rank']
    points_base = alt.Chart(points_data) 

    # 3. Lines Layer
    lines = base.mark_line().encode(
        x=alt.X('Week Type:N', sort=X_AXIS_ORDER, title='Week Rank Type', 
                axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Rank Value:Q', scale=y_scale, title='Chart Rank'),
        detail='Song Details:N',
        color=color_encoding,
        tooltip=['Song Details', 'Week Type', 'Rank Value']
    )
    
    # 4. Points Layer (Uses filtered data)
    points = points_base.mark_circle(size=100).encode(
        x=alt.X('Week Type:N', sort=X_AXIS_ORDER), 
        y=alt.Y('Rank Value:Q', scale=y_scale),
        color=color_encoding,
        size=alt.Size('Change:Q', legend=None), 
        tooltip=['Song Details', 'Week Type', 'Rank Value', 'Change']
    )

    chart = (lines + points).interactive()
    st.altair_chart(chart, use_container_width=True)


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