import re
from typing import List
from ChartData import ChartData
from bs4 import BeautifulSoup
from bs4.element import ResultSet
import requests

def get_artistsList(artistsSpan) -> list[str]:
    raw_segments: list[str] = [t.strip() for t in artistsSpan.stripped_strings if t.strip()]
    
    if len(raw_segments) <= 1:
        if not ("Featuring" in raw_segments[0]):
            return [raw_segments[0].strip()]
        else:
            return [s.strip() for s in raw_segments[0].split("Featuring")]
    
    def split_artist_segment(text) -> list[str]:
        parts = []
        
        # Split on 'Featuring' or 'ft.' (only if followed by something)
        feat_pattern = re.compile(r'\b(?:featuring|ft\.)\b', re.IGNORECASE)
        if feat_pattern.search(text):
            left, *right = feat_pattern.split(text, 1)
            left, right = left.strip(), right[0].strip() if right else ''
            if left:
                parts.append(left)
            if right:
                parts.append(right)
            return parts
        
        # Handle '&' logic
        amp_count = text.count('&')
        if amp_count > 1:
            # Multiple '&' means remove only the first one (band name case)
            text = text.replace('&', '', 1).strip()
            return [text]
        elif amp_count == 1:
            # Single '&' means split into two artists
            subparts = [p.strip() for p in text.split('&') if p.strip()]
            parts.extend(subparts)
            return parts
        
        return [text]

    # Step 3: apply the splitting to each segment
    artistsList = []
    for seg in raw_segments:
        artistsList.extend(split_artist_segment(seg))
        
    restricted_set = set(",", "x", "With")
        
    artistsList: list[str] = [a.replace(",", "").strip() for a in artistsList 
                              if a and a.strip() not in restricted_set]
    
    return artistsList

def __get_chart_info(rank: int, chart_result: ResultSet) -> ChartData:
    title = chart_result.find("h3", id="title-of-a-story").text.strip()
    
    artistsSpan = chart_result.find("span", class_="a-no-trucate")
    artistsText = artistsSpan.text.strip().replace("Featuring", "ft.")
    artistsList = get_artistsList(artistsSpan)

    song_stats = chart_result.find_all("span", class_="u-font-size-12")

    last_week = song_stats[1].text.strip()
    last_week = int(last_week) if last_week.isdigit() else None

    peak_pos = int(song_stats[3].text.strip())
    total_weeks = int(song_stats[5].text.strip())

    return ChartData(rank, title, artistsText, artistsList, last_week, peak_pos, total_weeks)

def get_chart_data(chart_str: str) -> List[dict[str, any]]:
    SITE_URL: str = f'https://www.billboard.com/charts/hot-100/{chart_str}'
    response = requests.get(SITE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    chart_results: ResultSet = soup.find_all('div', class_='o-chart-results-list-row-container')
    chart_entries = [
        __get_chart_info(rank, chart_result).get_dict()
        for rank, chart_result in enumerate(chart_results, 1)
    ]
    return chart_entries