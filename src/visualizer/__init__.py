from .logic.overall import get_team_win_lose, team_buy_type_win, get_player_stats
from .overall import plot_team_win_lose, plot_player_stats


class Visualizer:
    team_buy_type_win = staticmethod(team_buy_type_win)

    get_team_win_lose = staticmethod(get_team_win_lose)
    plot_team_win_lose = staticmethod(plot_team_win_lose)

    get_player_stats = staticmethod(get_player_stats)
    plot_player_stats = staticmethod(plot_player_stats)
