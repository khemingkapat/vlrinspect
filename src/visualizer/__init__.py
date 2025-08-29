from .logic.team import team_buy_type_win
from .logic.overall import get_team_win_lose
from .overall import plot_team_win_lose


class Visualizer:
    team_buy_type_win = staticmethod(team_buy_type_win)
    get_team_win_lose = staticmethod(get_team_win_lose)
    plot_team_win_lose = staticmethod(plot_team_win_lose)
