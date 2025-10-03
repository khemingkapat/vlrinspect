import plotly.express as px
from plotly.graph_objects import Figure
from models import MatchHistory
from .logic.overview import (
    get_team_buy_type_win_lose,
    get_team_win_condition,
    get_team_win_lose,
    get_team_pistol_impact,
)


def plot_team_win_lose(matches: MatchHistory) -> Figure:
    df = get_team_win_lose(matches).reset_index()

    fig = px.sunburst(
        df,
        path=["result", "map_name"],  # Inner = win/lose, Outer = map
        values="winner",
        color="result",
        color_discrete_map={"win": "#4ECDC4", "lose": "#FF6B6B"},
        title=f"{matches.full_name}'s Win/Lose Probabilities",
    )

    fig.update_layout(
        title_font_size=16,
        title_x=0.5,
        font_size=11,
    )

    fig.update_traces(textinfo="label+percent parent")

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


def plot_team_poistol_impact(matches: MatchHistory) -> Figure:
    team_pistol_impact = get_team_pistol_impact(matches).T
    team_pistol_impact.index.name = "round_type"
    df_melted = team_pistol_impact.reset_index().melt(
        id_vars="round_type",
        value_vars=["prob"],
        var_name="metric",
        value_name="probability",
    )

    # Format the round_type labels to be more readable
    label_map = {
        "pistol": "Pistol Round",
        "second_round": "Second Round",
        "2_round": "2 Round",
    }
    df_melted["round_type_label"] = df_melted["round_type"].map(label_map)

    fig = px.bar(
        df_melted,
        x="probability",  # Swapped: probability on x-axis
        y="round_type_label",  # Use formatted labels
        color="round_type",
        color_discrete_map={
            "pistol": "#FF6B6B",
            "second_round": "#4ECDC4",
            "2_round": "#45B7D1",
        },
        title=f"{matches.full_name}'s Pistol Impact",
        labels={"round_type_label": "Round Type", "probability": "Win Probability"},
        hover_data={"probability": ":.2f"},
        orientation="h",  # Horizontal orientation
    )
    fig.update_layout(
        xaxis_title="Win Probability",
        yaxis_title="Round Type",
        margin=dict(l=120, r=100, t=60, b=40),  # Increased right margin from 80 to 100
        height=350,
        yaxis=dict(
            tickmode="linear",
            tickangle=0,
        ),
        showlegend=False,
    )

    fig.update_traces(
        texttemplate="%{x:.2%}",
        textposition="outside",
        textfont_size=12,
        cliponaxis=False,  # This allows text to extend beyond the plot area
    )

    return fig
