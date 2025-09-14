from re import Match
import plotly.express as px
from plotly.graph_objects import Figure
import pandas as pd
from models import MatchHistory
from .logic.overall import (
    get_team_buy_type_win_lose,
    get_team_win_condition,
    get_team_win_lose,
)


def plot_team_win_lose(matches: MatchHistory) -> Figure:
    df = get_team_win_lose(matches)
    fig = px.pie(
        df,
        names="outcome",
        values="count",
        title=f"{matches.full_name}'s Win/Loss Ratio",
        hole=0.4,
        color="outcome",
        color_discrete_map={"win": "green", "lose": "red"},
    )
    return fig


def plot_team_buy_type_win_lose(matches: MatchHistory) -> Figure:
    df = get_team_buy_type_win_lose(matches)

    df_normalized = (
        df.div(df["total"], axis=0)
        .drop(columns=["total"])
        .sort_values("win", ascending=False)
    )

    df_normalized = df_normalized.reset_index()

    df_melted = df_normalized.melt(
        id_vars="winner_buytype", var_name="result", value_name="proportion"
    )

    fig = px.bar(
        df_melted,
        x="winner_buytype",
        y="proportion",
        color="result",
        color_discrete_map={"win": "#4ECDC4", "lose": "#FF6B6B"},
        title=f"{matches.full_name}'s Win/Lose Probabilities by Buy Type",
        labels={
            "winner_buytype": "Buy Type",
            "proportion": "Proportion",
            "result": "Result",
        },
    )

    fig.update_layout(
        title_font_size=16,
        title_x=0.5,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        legend_title_font_size=12,
        font_size=11,
        height=500,
        yaxis=dict(range=[0, 1], tickformat=".1%"),
        barmode="stack",
    )

    fig.update_xaxes(tickangle=45)

    return fig


def plot_team_win_condition(matches: MatchHistory) -> Figure:
    df = get_team_win_condition(matches)

    df_normalized = (
        df.div(df["total"], axis=0)
        .drop(columns=["total"])
        .sort_values("win", ascending=False)
    )

    df_normalized = df_normalized.reset_index()
    df_melted = df_normalized.melt(
        id_vars="reason", var_name="result", value_name="proportion"
    )

    fig = px.bar(
        df_melted,
        x="reason",
        y="proportion",
        color="result",
        color_discrete_map={"win": "#4ECDC4", "lose": "#FF6B6B"},
        title=f"{matches.full_name}'s Win/Lose Probabilities by Buy Type",
        labels={
            "winner_buytype": "Buy Type",
            "proportion": "Proportion",
            "result": "Result",
        },
    )

    fig.update_layout(
        xaxis_title="Reason",
        yaxis_title="Number of Rounds",
        legend_title_text="Result",
        font=dict(family="Arial, sans-serif", size=12, color="#333"),
    )

    return fig
