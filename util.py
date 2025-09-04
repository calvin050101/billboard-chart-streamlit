from ChartData import ChartData
from bs4 import BeautifulSoup
import requests

def __get_chart_info(rank, chart_result):
    title = chart_result.find("h3", id="title-of-a-story").text.strip()
    artists: str = chart_result.find("span", class_="a-no-trucate").text.strip()\
                    .replace("Featuring", "ft.")

    song_stats = chart_result.find_all("span", class_="u-font-size-12")

    last_week = song_stats[1].text.strip()
    last_week = int(last_week) if last_week.isdigit() else None

    peak_pos = int(song_stats[3].text.strip())
    total_weeks = int(song_stats[5].text.strip())

    return ChartData(rank, title, artists, last_week, peak_pos, total_weeks)

def get_chart_data(chart_str: str):
    SITE_URL = f'https://www.billboard.com/charts/hot-100/{chart_str}'
    response = requests.get(SITE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    chart_results = soup.find_all('div', class_='o-chart-results-list-row-container')
    chart_entries = [
        __get_chart_info(rank, chart_result).get_dict()
        for rank, chart_result in enumerate(chart_results, 1)
    ]
    return chart_entries