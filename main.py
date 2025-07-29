import streamlit as st
import billboard
import pandas as pd
import datetime


def replace_strings(original_string, replacement_dict):
    """Efficiently replace words in a string based on a dictionary."""
    return ' '.join(replacement_dict.get(word, word) for word in original_string.split())


def get_change_status(song_item):
    """Returns change value based on song's rank and position."""
    if song_item.lastPos == 0:
        return "NEW" if song_item.isNew else "RE"

    change = song_item.lastPos - song_item.rank
    if change == 0:
        return "="
    elif change > 0:
        return f"+{change}"
    else:
        return str(change)


def get_hot_100_chart_dataframe(date_str):
    """
    Returns a pandas DataFrame of the Billboard Hot 100 chart for a given date (YYYY-MM-DD).
    """
    chart = billboard.ChartData('hot-100', date=date_str)

    data = [
        {
            "Rank": song.rank,
            "Title": song.title,
            "Artist": replace_strings(song.artist, {"Featuring": "ft.", "With": "with"}),
            "Change": get_change_status(song),
            "Last Position": song.lastPos or "-",
            "Peak Position": song.peakPos,
            "Weeks on Chart": song.weeks
        } for song in chart
    ]

    return pd.DataFrame(data)


# --- Streamlit UI ---
st.set_page_config(page_title="🎵 Billboard Hot 100 Viewer", layout="centered")

st.title("🎵 Billboard Hot 100 Chart Viewer")
st.markdown("Enter a date to view the Billboard Hot 100 chart for that week.")

selected_date = st.date_input(
    "Select a date",
    value=datetime.date.today(),
    min_value=datetime.date(1958, 8, 4),
    max_value=datetime.date.today()
)


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
    st.subheader("🏆 Top 100")
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

    # Show Re-peaks and Peakers
    peakers = df.loc[
        (df["Rank"] == df["Peak Position"]) &
        (df["Change"].str.startswith(("+", "^"))), :
    ]
    if not peakers.empty:
        st.subheader("⛰️ Peakers (New Peak or Re-Peak)")
        st.dataframe(peakers.reset_index(drop=True), use_container_width=True)

    # Show Gainers (10+ positions up)
    gainers = df.loc[df["Change"].str.startswith("+"), :].copy()
    if not gainers.empty:
        gainers.loc[:, "Change Int"] = gainers["Change"].str.extract(r"\+(\d+)").astype(float)
        big_gainers = gainers.loc[gainers["Change Int"] >= 10, :].drop(columns="Change Int")
        if not big_gainers.empty:
            st.subheader("📈 Gainers (10+ Spots Up)")
            st.dataframe(big_gainers.reset_index(drop=True), use_container_width=True)

    # Show Losers (10+ positions down)
    losers = df.loc[df["Change"].str.startswith("-"), :].copy()
    if not losers.empty:
        losers.loc[:, "Change Int"] = losers["Change"].astype(int).abs()
        big_losers = losers.loc[losers["Change Int"] >= 10, :].drop(columns="Change Int")
        if not big_losers.empty:
            st.subheader("📉 Losers (10+ Spots Down)")
            st.dataframe(big_losers.reset_index(drop=True), use_container_width=True)

    # Show RE-entries
    re_entries = df.loc[df["Change"] == "RE", :].drop(columns=['Change', 'Last Position'])
    if not re_entries.empty:
        st.subheader("🔁 Re-Entries This Week")
        st.dataframe(re_entries.reset_index(drop=True), use_container_width=True)

    # Show NEW entries
    new_entries = df.loc[df["Change"] == "NEW", :] \
        .drop(columns=['Change', 'Last Position', 'Peak Position', 'Weeks on Chart'])
    if not new_entries.empty:
        st.subheader("🆕 New Entries This Week")
        st.dataframe(new_entries.reset_index(drop=True), use_container_width=True)

    # Show dropouts section if any
    if not dropouts.empty:
        st.subheader("🚪 Dropouts (Songs that left the chart)")
        st.dataframe(dropouts.reset_index(drop=True), use_container_width=True)


if st.button("Get Chart"):
    date_str = selected_date.strftime("%Y-%m-%d")
    with st.spinner(f"Fetching chart for {date_str}..."):
        try:
            displayData(date_str)
        except Exception as e:
            st.error(f"Error fetching chart: {e}")