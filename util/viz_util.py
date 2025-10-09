import pandas as pd

# Custom order for longevity categories (used in plot_total_weeks_distribution)
LONGEVITY_ORDER = ['1-5 Weeks', '6-15 Weeks', '16-30 Weeks', '31-45 Weeks', 
                   '46-60 Weeks', '61+ Weeks']

def categorize_change(change_str):
    """Categorizes the 'Change' string into 'Up', 'Down', 'Same', 'Return', 'New'."""
    if pd.isna(change_str):
        return "Unknown"
    
    change_str = str(change_str).strip()

    if change_str == "NEW":
        return "New"
    elif change_str == "RE":
        return "Return"
    elif change_str == "=":
        return "Same"
    elif change_str.startswith("-"):
        try:
            val = int(change_str)
            return "Down" if val < 0 else "Same"
        except ValueError:
            return "Unknown"
    elif change_str.isdigit():
        try:
            val = int(change_str)
            return "Up" if val > 0 else "Same"
        except ValueError:
            return "Unknown"
    else:
        return "Unknown"
    
def categorize_longevity(df):
    """
    Categorizes songs based on their total weeks on the chart using pd.cut for 
    a more pythonic and efficient approach.
    """
    # Define the bin boundaries (must be one more than the number of labels)
    # The bins are set to capture the ranges: (0, 5], (5, 15], (15, 30], (30, infinity]
    bins = [0, 5, 15, 30, 45, 60, float('inf')]
    
    # Use pd.cut to segment the 'Total Weeks' column
    df['Longevity Category'] = pd.cut(
        df['Total Weeks'],
        bins=bins,
        labels=LONGEVITY_ORDER,
        include_lowest=True,
        right=True
    )
    return df

# Helper functions to prepare data for visualizations
def get_week_distribution_data(df):
    plot_data = categorize_longevity(df.copy())
    
    return (
        plot_data.groupby('Longevity Category', observed=True)
        .size()
        .reset_index(name='Count')
    )

def get_peak_vs_weeks_data(df):
    plot_data = df.copy()
    plot_data['Change Category'] = plot_data['Change'].apply(categorize_change)

    return plot_data.dropna(subset=['Total Weeks', 'Peak Position', 'Title', 'Change Category'])

def get_position_change_distribution_data(df):
    change_data = df[~df['Change'].isin(['NEW', 'RE', '='])].copy()
    change_data['Position Change Value'] = pd.to_numeric(change_data['Change'], errors='coerce')
    return change_data.dropna(subset=['Position Change Value']).copy()