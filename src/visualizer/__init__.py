from .logic.overall import (
    get_team_pistol_impact,
    get_team_win_lose,
    get_team_buy_type_win_lose,
    get_team_win_condition,
)

from .logic.player import (
    get_players_agent_pool,
    get_player_stats,
    get_player_stat_history,
)

from .overall import (
    plot_team_win_condition,
    plot_team_win_lose,
    plot_team_buy_type_win_lose,
    plot_team_poistol_impact,
)

from .player import plot_players_agent_pool, plot_player_stats, plot_player_stat_history

from .logic.map import (
    get_team_pick_ban,
    get_team_side_bias,
    get_map_pistol_impact,
    get_players_map_agent_pool,
)
from .map import (
    plot_team_pick_ban,
    plot_team_side_bias,
    plot_map_pistol_impact,
    plot_players_map_agent_pool,
)


class Visualizer:

    # overall
    get_team_win_lose = staticmethod(get_team_win_lose)
    plot_team_win_lose = staticmethod(plot_team_win_lose)

    get_team_buy_type_win_lose = staticmethod(get_team_buy_type_win_lose)
    plot_team_buy_type_win_lose = staticmethod(plot_team_buy_type_win_lose)

    get_team_win_condition = staticmethod(get_team_win_condition)
    plot_team_win_condition = staticmethod(plot_team_win_condition)

    get_team_pistol_impact = staticmethod(get_team_pistol_impact)
    plot_team_pistol_impact = staticmethod(plot_team_poistol_impact)

    # player
    get_player_stats = staticmethod(get_player_stats)
    plot_player_stats = staticmethod(plot_player_stats)

    get_players_agent_pool = staticmethod(get_players_agent_pool)
    plot_players_agent_pool = staticmethod(plot_players_agent_pool)

    get_player_stat_history = staticmethod(get_player_stat_history)
    plot_player_stat_history = staticmethod(plot_player_stat_history)

    # map
    get_team_pick_ban = staticmethod(get_team_pick_ban)
    plot_team_pick_ban = staticmethod(plot_team_pick_ban)

    get_players_map_agent_pool = staticmethod(get_players_map_agent_pool)
    plot_players_map_agent_pool = staticmethod(plot_players_map_agent_pool)

    get_team_side_bias = staticmethod(get_team_side_bias)
    plot_team_side_bias = staticmethod(plot_team_side_bias)

    get_map_pistol_impact = staticmethod(get_map_pistol_impact)
    plot_map_pistol_impact = staticmethod(plot_map_pistol_impact)
