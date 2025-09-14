from models import MatchHistory
from plotly.graph_objects import Figure
import plotly.express as px
from .logic.player import get_player_stats, get_player_stat_history
import pandas as pd


def sort_players_by_stat(df, stat, sort_by, sort_order):
    if sort_by == "alphabetical":
        player_order = sorted(df["name"].unique())
    else:
        pivot_df = df.pivot(index="name", columns="cat", values=stat).fillna(0)

        if sort_by == "mean":
            sort_values = pivot_df.mean(axis=1)
        elif sort_by in pivot_df.columns:
            sort_values = pivot_df[sort_by]
        else:
            sort_values = pivot_df.mean(axis=1)

        ascending = sort_order == "asc"
        player_order = sort_values.sort_values(ascending=ascending).index.tolist()

    return player_order


def plot_player_stats(
    matches: MatchHistory,
    category_type: str = "side",
    stat_column: str = "Rating 2.0",
    sort_by: str = "mean",
    sort_order: str = "asc",
) -> Figure:
    """
    Simplified function that creates a single bar chart based on parameters.
    All interactivity is handled by Streamlit components.
    """
    df = get_player_stats(matches, cat_by=category_type)

    stats_columns = [
        col
        for col in df.columns
        if col not in ["name", "cat"] and df[col].dtype in ["float64", "int64"]
    ]

    if stat_column not in stats_columns:
        stat_column = stats_columns[0]

    if category_type == "side":
        color_map = {"atk": "#FF6B6B", "def": "#4ECDC4"}
        title_suffix = "Side"
    else:
        color_map = {"lose": "#FF6B6B", "win": "#4ECDC4"}
        title_suffix = "Win/Lose"

    player_order = sort_players_by_stat(df, stat_column, sort_by, sort_order)
    df_sorted = df.copy()
    df_sorted["name"] = pd.Categorical(
        df_sorted["name"], categories=player_order, ordered=True
    )
    df_sorted = df_sorted.sort_values("name")

    fig = px.bar(
        df_sorted,
        x=stat_column,
        y="name",
        color="cat",
        barmode="group",
        title=f"{matches.full_name}'s Player Comparison - {stat_column} ({title_suffix}, sorted by {sort_by})",
        labels={"name": "Player", "cat": "Category"},
        color_discrete_map=color_map,
        hover_data={"name": True, "cat": True, stat_column: ":.2f"},
        orientation="h",
    )

    fig.update_layout(height=500, margin=dict(t=80, b=50, l=50, r=50))

    return fig


def plot_player_stat_history(
    matches: MatchHistory, stat_column: str = "Rating 2.0"
) -> Figure:
    player_stat_history = get_player_stat_history(matches, stat_column)
    names = player_stat_history.columns

    df_reset = player_stat_history.reset_index()
    df_reset["game_index"] = range(len(df_reset))

    melted_df = df_reset.melt(
        id_vars=["game_id", "game_index"],
        value_vars=names,
        var_name="player",
        value_name="score",
    )
    print(melted_df)

    fig = px.line(
        melted_df,
        x="game_index",
        y="score",
        color="player",
        title="Player Performance Across Games",
        labels={"score": "Performance Score", "game_index": "Game Sequence"},
        markers=True,
        color_discrete_sequence=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"],
    )

    fig.update_layout(
        xaxis_title="Game ID",
        yaxis_title="Performance Score",
        legend_title="Player",
        hovermode="x unified",
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(df_reset))),  # All positions
            ticktext=[str(gid) for gid in df_reset["game_id"]],  # All game_ids
            tickangle=45,
        ),
    )

    fig.update_traces(
        line=dict(width=2.5),
        hovertemplate="<b>%{fullData.name}</b><br>"
        + "Game ID: %{customdata[0]}<br>"
        + "Value: %{y:.2f}<extra></extra>",
    )

    for trace in fig.data:
        player_data = melted_df[melted_df["player"] == trace.name]
        trace.customdata = player_data[["game_id"]].values

    return fig
