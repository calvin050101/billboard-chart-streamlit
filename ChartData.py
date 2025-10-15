class ChartData:
    def __init__(
            self, rank: int, title: str, artists: str, artistsList: list[str],
            last_week: int | None, peak_pos: int, total_weeks: int
        ):
        self.rank = rank
        self.title = title
        self.artists = artists
        self.artistsList = artistsList
        self.peak_pos = peak_pos
        self.total_weeks = total_weeks
        self.last_week = last_week or None

        self.change = ""
        if self.last_week is None:
            self.change = "RE" if self.total_weeks > 1 else "NEW"
        else:
            pos_change = self.last_week - self.rank
            self.change = "=" if pos_change == 0 else str(pos_change)
    
    def get_dict(self) -> dict[str, any]:
        return {
            "Rank": self.rank,
            "Title": self.title,
            "Artists": self.artists,
            "Artists List": self.artistsList,
            "Change": self.change,
            "Last Week": self.last_week,
            "Peak Position": self.peak_pos,
            "Total Weeks": self.total_weeks
        }
