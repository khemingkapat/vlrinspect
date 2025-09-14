from models.match_history import MatchHistory
from .logic.map import get_team_pick_ban, get_team_side_bias
from plotly.graph_objects import Figure
import plotly.express as px


def plot_team_pick_ban(matches: MatchHistory) -> Figure:
    team_pick_ban = get_team_pick_ban(matches).reset_index()

    melted_df = team_pick_ban.melt(
        id_vars=["map"],
        value_vars=["pick", "ban"],
        var_name="action",
        value_name="count",
    )

    fig = px.bar(
        melted_df,
        x="map",
        y="count",
        color="action",
        barmode="group",
        color_discrete_map={"ban": "#FF6B6B", "pick": "#4ECDC4"},
        title=f"{matches.full_name}'s Pick and Ban Counts by Map",
        labels={"count": "Count", "map": "Map", "action": "Action"},
    )

    return fig


def plot_team_side_bias(matches: MatchHistory) -> Figure:
    team_side_win = get_team_side_bias(matches).reset_index().sort_values("win_rate")

    fig = px.bar(
        team_side_win,
        x="map",
        y="win_rate",
        color="team_side",
        color_discrete_map={"atk": "#FF6B6B", "def": "#4ECDC4"},
        barmode="group",
        title=f"{matches.full_name}'s Side Bias",
        labels={"win_rate": "Win Rate (%)", "map": "Map", "team_side": "Side"},
    )
    return fig
