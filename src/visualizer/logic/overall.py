from models import MatchHistory
import pandas as pd


def get_team_win_lose(matches: MatchHistory) -> pd.DataFrame:
    win_lose_count = matches.matches_data["result"].value_counts().reset_index()
    win_lose_count.columns = ["outcome", "count"]
    return win_lose_count
