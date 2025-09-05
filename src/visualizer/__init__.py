from .logic.overall import (
    get_team_win_lose,
    get_team_buy_type_win_lose,
    get_player_stats,
    get_team_win_condition,
)
from .overall import (
    plot_team_win_condition,
    plot_team_win_lose,
    plot_player_stats,
    plot_team_buy_type_win_lose,
)


class Visualizer:

    # overall
    get_team_win_lose = staticmethod(get_team_win_lose)
    plot_team_win_lose = staticmethod(plot_team_win_lose)

    get_player_stats = staticmethod(get_player_stats)
    plot_player_stats = staticmethod(plot_player_stats)

    get_team_buy_type_win_lose = staticmethod(get_team_buy_type_win_lose)
    plot_team_buy_type_win_lose = staticmethod(plot_team_buy_type_win_lose)

    get_team_win_condition = staticmethod(get_team_win_condition)
    plot_team_win_condition = staticmethod(plot_team_win_condition)
