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

def get_top_10_line_chart_data(df, df_last_week):
    # 1. Identify current Top 10
    top_10_titles = df[df['Rank'] <= 10]['Title'].tolist()
    if not top_10_titles:
        return pd.DataFrame(), [] # Return empty dataframes if no Top 10

    # 2. Extract current week data for Top 10
    current_week_data = (
        df[df['Title'].isin(top_10_titles)]
        [['Title', 'Artists', 'Rank', 'Change']]
        .copy()
    )
    current_week_data.rename(columns={'Rank': 'Current Rank'}, inplace=True)

    # 3. Extract last week data for Top 10 songs
    last_week_data = (
        df_last_week[df_last_week['Title'].isin(top_10_titles)]
        [['Title', 'Artists', 'Rank']]
        .copy()
    )
    last_week_data.rename(columns={'Rank': 'Previous Rank'}, inplace=True)

    # 4. Merge the data
    comparison_data = current_week_data.merge(last_week_data, on=['Title', 'Artists'], how='left')

    # 5. Convert to Long Format (stacking ranks)
    rank_comparison_long = pd.melt(
        comparison_data,
        id_vars=['Title', 'Artists', 'Change'],
        value_vars=['Previous Rank', 'Current Rank'],
        var_name='Week Type',
        value_name='Rank Value'
    ).dropna(subset=['Rank Value'])

    # 6. Create combined song details column
    rank_comparison_long['Song Details'] = rank_comparison_long['Title'] + ' - ' + rank_comparison_long['Artists']

    return rank_comparison_long, top_10_titles

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