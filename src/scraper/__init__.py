from src.scraper.history import (
    get_team_history_list,
    scrape_matches,
    scrape_match_info,
    extract_overview_from_html,
    extract_round_result_from_html,
    extract_economy_from_html,
)
from src.scraper.team import get_teams_from_match
from src.scraper.upcoming import get_upcoming_matches
import requests


class Scraper:
    get_upcoming_matches = staticmethod(get_upcoming_matches)
    get_teams_from_match = staticmethod(get_teams_from_match)
    get_team_history_list = staticmethod(get_team_history_list)
    scrape_match_info = staticmethod(scrape_match_info)
    extract_economy_from_html = staticmethod(extract_economy_from_html)
    extract_round_result_from_html = staticmethod(extract_round_result_from_html)
    extract_df_from_html = staticmethod(extract_overview_from_html)

    @staticmethod
    def get_team_history(
        _session: requests.Session,
        match_url: str,
        head: int = -1,
        url: str = "https://www.vlr.gg/",
    ):
        team1, team2 = get_teams_from_match(_session, match_url)
        team1_hist_list, team1_abbr = get_team_history_list(_session, team1)
        team2_hist_list, team2_abbr = get_team_history_list(_session, team2)

        team_abbr = team1_abbr | team2_abbr

        team1_hist = scrape_matches(
            _session,
            matches_url=team1_hist_list,
            head=head,
            team_abbreviate=team_abbr,
            full_name=list(team1_abbr.keys())[0],
        )
        team2_hist = scrape_matches(
            _session,
            matches_url=team2_hist_list,
            head=head,
            team_abbreviate=team_abbr,
            full_name=list(team2_abbr.keys())[0],
        )

        return team1_hist, team2_hist
