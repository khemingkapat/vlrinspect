from models.match_history import MatchHistory
from .logic.map import get_team_pick_ban, get_team_side_bias, get_map_pistol_impact
from plotly.graph_objects import Figure
import plotly.express as px
import pandas as pd


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


def plot_map_pistol_impact(matches: MatchHistory) -> Figure:
    map_pistol_impact = get_map_pistol_impact(matches)

    map_pistol_prob = (
        map_pistol_impact.xs("prob", level="type")
        .sort_values("pistol", ascending=False)
        .reset_index()
    )

    map_pistol_total = (
        map_pistol_impact.xs("total", level="type")
        .reindex(map_pistol_prob["map_name"])
        .reset_index()
    )

    map_pistol_wins = (
        map_pistol_impact.xs("win", level="type")
        .reindex(map_pistol_prob["map_name"])
        .reset_index()
    )

    df_melted = pd.melt(
        map_pistol_prob,
        id_vars=["map_name"],
        value_vars=["pistol", "second_round", "2_round"],
        var_name="round_type",
        value_name="win_probability",
    )

    df_total_melted = pd.melt(
        map_pistol_total,
        id_vars=["map_name"],
        value_vars=["pistol", "second_round", "2_round"],
        var_name="round_type",
        value_name="total_rounds",
    )

    df_wins_melted = pd.melt(
        map_pistol_wins,
        id_vars=["map_name"],
        value_vars=["pistol", "second_round", "2_round"],
        var_name="round_type",
        value_name="rounds_won",
    )

    df_combined = df_melted.merge(df_total_melted, on=["map_name", "round_type"]).merge(
        df_wins_melted, on=["map_name", "round_type"]
    )

    fig = px.bar(
        df_combined,
        x="map_name",
        y="win_probability",
        color="round_type",
        barmode="group",
        title=f"{matches.full_name}'s Pistol Impact by Map",
        labels={
            "map_name": "Map Name",
            "win_probability": "Win Probability",
            "round_type": "Round Type",
        },
        color_discrete_map={
            "pistol": "#FF6B6B",
            "second_round": "#4ECDC4",
            "2_round": "#45B7D1",
        },
        hover_data={
            "total_rounds": True,
            "rounds_won": True,
            "win_probability": ":.1%",  # Format as percentage
        },
        custom_data=["total_rounds", "rounds_won"],
    )

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>"
        + "Round Type: %{fullData.name}<br>"
        + "Win Rate: %{y:.1%}<br>"
        + "Rounds Won: %{customdata[1]:.0f}<br>"
        + "Total Rounds: %{customdata[0]:.0f}<br>"
        + "<extra></extra>"
    )

    return fig
