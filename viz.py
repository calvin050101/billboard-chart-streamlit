import streamlit as st
import pandas as pd
import altair as alt

def categorize_change(change_str):
    """Categorizes the 'Change' string into 'Up', 'Down', 'Same', 'Return', 'New'."""
    if pd.isna(change_str): # Handle potential NaN values from get_chart_data
        return "Unknown"
    
    change_str = str(change_str).strip() # Ensure it's a string and clean it

    if change_str == "NEW":
        return "New"
    elif change_str == "RE":
        return "Return"
    elif change_str == "=":
        return "Same"
    elif change_str.startswith("-"):
        # Check if it's a valid number after '-'
        try:
            val = int(change_str)
            return "Down" if val < 0 else "Same" # Should be Down, but handle 0 defensively
        except ValueError:
            return "Unknown" # Handle cases like "-10_bad"
    elif change_str.isdigit(): # e.g., "5", "10" (means +5, +10)
        try:
            val = int(change_str)
            return "Up" if val > 0 else "Same" # Should be Up, but handle 0 defensively
        except ValueError:
            return "Unknown"
    else:
        return "Unknown" # For any other unexpected values


def plot_peak_vs_weeks(df):
    """
    Creates and displays a scatter plot of Peak Position vs. Total Weeks,
    with colors classified by position changes.
    Assumes df columns 'Total Weeks' and 'Peak Position' are numeric.
    """
    st.subheader("Peak Position vs. Total Weeks on Chart")
    
    # Create the 'Change Category' column
    plot_data = df.copy() # Work on a copy to avoid SettingWithCopyWarning
    plot_data['Change Category'] = plot_data['Change'].apply(categorize_change)

    # Filter out NaNs for plotting relevant columns
    plot_data = plot_data.dropna(subset=['Total Weeks', 'Peak Position', 'Title', 'Change Category'])
    
    # Define a custom color scheme for better distinction
    color_scale = alt.Scale(
        domain=["Up", "Down", "Same", "Return", "New", "Unknown"],
        range=["#2ca02c", "#d62728", "#1f77b4", "#ff7f0e", "#9467bd", "#8c8c8c"] # Green, Red, Blue, Orange, Purple, Grey
    )

    if not plot_data.empty:
        scatter_chart = alt.Chart(plot_data).mark_circle(size=80).encode(
            x=alt.X('Total Weeks:Q', title='Total Weeks on Chart'),
            y=alt.Y('Peak Position:Q', scale=alt.Scale(reverse=True), title='Peak Position'),
            tooltip=['Title', 'Artists', 'Total Weeks', 'Peak Position', 'Rank', 'Change', 'Change Category'],
            color=alt.Color('Change Category:N', scale=color_scale, title='Position Change'), # Use the new category for color
            order=alt.Order('Change Category', sort='descending') # Optional: Ensure consistent legend order
        ).properties(
            width='container',
            height=400
        ).interactive() 
        
        st.altair_chart(scatter_chart, use_container_width=True)
    else:
        st.info("No data available to generate the Peak Position vs. Total Weeks plot.")

def plot_position_change_histogram(df):
    """
    Creates and displays a histogram of position changes, excluding NEW, RE, and =.
    """
    st.subheader("Distribution of Position Changes")
    
    # Filter out 'NEW', 'RE', and '='
    change_data = df[~df['Change'].isin(['NEW', 'RE', '='])].copy()
    
    # Convert 'Change' column to numeric.
    change_data['Position Change Value'] = pd.to_numeric(change_data['Change'], errors='coerce')
    
    # Drop rows where conversion failed
    change_data = change_data.dropna(subset=['Position Change Value'])

    if not change_data.empty:
        hist_chart = alt.Chart(change_data).mark_bar().encode(
            x=alt.X('Position Change Value:Q', bin=alt.Bin(step=5), title='Position Change (Spots)'),
            y=alt.Y('count():Q', title='Number of Songs'),
            tooltip=[alt.Tooltip('Position Change Value:Q', bin=True, title='Position Change Range'), 'count():Q'],
            color=alt.value("teal")
        ).properties(
            width='container',
            height=400
        )
        
        # Add text labels
        text = hist_chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-4
        ).encode(
            text=alt.Text('count():Q'),
            tooltip=[]
        )

        st.altair_chart(hist_chart + text, use_container_width=True)
    else:
        st.info("No data available to generate the Position Changes histogram (all songs were NEW, RE, or =).")