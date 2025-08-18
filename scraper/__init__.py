from scraper.history import get_team_history_list, scrape_matches, scrape_match_info
from .team import get_teams_from_match
from .upcoming import get_upcoming_matches
import requests


class Scraper:
    get_upcoming_matches = staticmethod(get_upcoming_matches)
    get_teams_from_match = staticmethod(get_teams_from_match)
    get_team_history_list = staticmethod(get_team_history_list)
    scrape_match_info = staticmethod(scrape_match_info)

    @staticmethod
    def get_team_history(
        _session: requests.Session,
        match_url: str,
        head: int = -1,
        url: str = "https://www.vlr.gg/",
    ):
        team1, team2 = get_teams_from_match(_session, match_url)
        team1_hist_list, team_1_abbr = get_team_history_list(_session, team1, head=head)
        team2_hist_list, team_2_abbr = get_team_history_list(_session, team2, head=head)
        # print(team1_hist_list)
        # print(team2_hist_list)

        team_abbr = team_1_abbr | team_2_abbr
        # print(team_abbr)

        team1_hist = scrape_matches(_session, team1_hist_list, team_abbr)
        team2_hist = scrape_matches(_session, team2_hist_list, team_abbr)
        print(team1_hist)
        print(team2_hist)
