import streamlit as st
import billboard
import pandas as pd
import datetime

ARTIST_REPLACEMENTS = {"Featuring": "ft.", "With": "with"}
MIN_DATE = datetime.date(1958, 8, 4) # First Billboard Hot 100 chart date
TODAY = datetime.date.today()

# --- Helper Functions ---
def replace_strings(original_string, replacement_dict):
    """Efficiently replace words in a string based on a dictionary."""
    return ' '.join(replacement_dict.get(word, word) for word in original_string.split())

def get_change_status(song_item):
    """Returns change value based on song's rank and last position."""
    if song_item.lastPos == 0:
        return "NEW" if song_item.isNew else "RE"

    change = song_item.lastPos - song_item.rank
    if change == 0:
        return "="
    elif change > 0:
        return f"+{change}"
    else:
        return str(change)

@st.cache_data(ttl=3600) # Cache data for 1 hour
def get_hot_100_chart_dataframe(date_str):
    """
    Returns a pandas DataFrame of the Billboard Hot 100 chart for a given date (YYYY-MM-DD).
    Caches the result to avoid redundant API calls.
    """
    try:
        chart = billboard.ChartData('hot-100', date=date_str)
        data = [
            {
                "Rank": song.rank,
                "Title": song.title,
                "Artist": replace_strings(song.artist, ARTIST_REPLACEMENTS),
                "Change": get_change_status(song),
                "Last Position": song.lastPos or "-",
                "Peak Position": song.peakPos,
                "Weeks on Chart": song.weeks
            } for song in chart
        ]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Could not retrieve chart for {date_str}. Please try a different date. Error: {e}")
        return pd.DataFrame()


def show_section(title, df):
    if not df.empty:
        st.subheader(title)
        st.dataframe(df.reset_index(drop=True), use_container_width=True)


# --- Streamlit UI ---
st.set_page_config(page_title="🎵 Billboard Hot 100 Viewer", layout="centered")

st.title("🎵 Billboard Hot 100 Chart Viewer")
st.markdown("Enter a date to view the Billboard Hot 100 chart for that week.")

selected_date = st.date_input("Select a date", value=TODAY, min_value=MIN_DATE, max_value=TODAY)

def displayData(date_str):
    global selected_date
    last_week_date = selected_date - datetime.timedelta(days=7)
    last_week_date_str = last_week_date.strftime("%Y-%m-%d")

    df = get_hot_100_chart_dataframe(date_str)
    df["Last Position"] = pd.to_numeric(df["Last Position"], errors="coerce")
    df_last_week = get_hot_100_chart_dataframe(last_week_date_str)

    # Find dropouts
    dropouts = df_last_week.loc[~df_last_week["Title"].isin(df["Title"]), ["Rank", "Title", "Artist"]]

    st.success(f"Billboard Hot 100 for {date_str}")
    show_section("🏆 Top 100", df)

    # Show Re-peaks and Peakers
    peakers = df.loc[
        (df["Rank"] == df["Peak Position"]) &
        (df["Change"].str.startswith(("+", "^"))), :
    ]
    show_section("⛰️ Peakers (New Peak or Re-Peak)", peakers)

    # Gainers: +10 or more
    gainers = df[df["Change"].str.startswith("+")].copy()
    gainers["Change Int"] = gainers["Change"].str.extract(r"\+(\d+)").astype(float)
    big_gainers = gainers[gainers["Change Int"] >= 10].drop(columns="Change Int")
    show_section("📈 Gainers (10+ Spots Up)", big_gainers)

    # Losers: -10 or more
    losers = df[df["Change"].str.startswith("-")].copy()
    losers["Change Int"] = losers["Change"].astype(int).abs()
    big_losers = losers[losers["Change Int"] >= 10].drop(columns="Change Int")
    show_section("📉 Losers (10+ Spots Down)", big_losers)

    # Re-entries
    re_entries = df[df["Change"] == "RE"].drop(columns=["Change", "Last Position"])
    show_section("🔁 Re-Entries This Week", re_entries)

    # New entries
    new_entries = df[df["Change"] == "NEW"].drop(
        columns=["Change", "Last Position", "Peak Position", "Weeks on Chart"]
    )
    show_section("🆕 New Entries This Week", new_entries)

    # Dropouts: Songs that were in last week's chart but not this week's
    dropouts = df_last_week[~df_last_week["Title"].isin(df["Title"])][["Rank", "Title", "Artist"]]
    show_section("🚪 Dropouts (Songs that left the chart)", dropouts)


if st.button("Get Chart"):
    date_str = selected_date.strftime("%Y-%m-%d")
    with st.spinner(f"Fetching chart for {date_str}..."):
        try:
            displayData(date_str)
        except Exception as e:
            st.error(f"Error fetching chart: {e}")