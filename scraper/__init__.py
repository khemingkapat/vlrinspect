from scraper.history import get_team_history
from .team import get_teams_from_match
from .upcoming import get_upcoming_matches


class Scraper:
    get_upcoming_matches = staticmethod(get_upcoming_matches)
    get_teams_from_match = staticmethod(get_teams_from_match)
    get_team_history = staticmethod(get_team_history)
