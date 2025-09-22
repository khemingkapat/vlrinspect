from models import MatchHistory
from plotly.graph_objects import Figure
import plotly.express as px
from .logic.player import (
    get_player_stats,
    get_player_stat_history,
    get_players_agent_pool,
)
import pandas as pd
import plotly.graph_objects as go
import base64
from pathlib import Path


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


def plot_players_agent_pool(matches: MatchHistory):
    player_agent_pool = get_players_agent_pool(
        matches, apply_composite_scores=True
    ).reset_index()
    all_cols = [
        col
        for col in player_agent_pool.columns
        if col not in ["index", "name", "agent", "game_id"]
    ]
    x_stat, y_stat = all_cols
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
    color_map = {
        player: colors[i] for i, player in enumerate(player_agent_pool.name.unique())
    }

    # Create agent emoji mapping instead of loading images
    agent_emoji_map = {
        "jett": "💨",
        "reyna": "👁️",
        "sage": "🌿",
        "phoenix": "🔥",
        "raze": "💣",
        "breach": "💥",
        "omen": "🥷🏾",
        "brimstone": "📱",
        "cypher": "📹",
        "sova": "🏹",
        "killjoy": "🤖",
        "viper": "🐍",
        "skye": "🦋",
        "yoru": "👤",
        "astra": "⭐",
        "kayo": "🔋",
        "chamber": "🎯",
        "neon": "⚡",
        "fade": "🐶",
        "harbor": "🌊",
        "gekko": "🦎",
        "deadlock": "🕷️",
        "iso": "🛡️",
        "clove": "🍀",
        "vyse": "🌵",
        "waylay": "⚡️",
        "tejo": "🚀",
    }

    # Add a column for the agent emoji
    player_agent_pool["agent_emoji"] = (
        player_agent_pool["agent"].str.lower().map(agent_emoji_map)
    )
    # Fill any missing emojis with question mark
    player_agent_pool["agent_emoji"] = player_agent_pool["agent_emoji"].fillna("❓")

    fig = go.Figure()

    # Calculate min and max game_id for size scaling
    min_games = player_agent_pool["game_id"].min()
    max_games = player_agent_pool["game_id"].max()

    # Define size range (minimum and maximum bubble sizes)
    min_size = 50  # Minimum bubble size
    max_size = 100  # Maximum bubble size

    # Function to scale bubble sizes with less drastic differences
    def scale_bubble_size(game_count):
        if max_games == min_games:
            return min_size
        # Use square root to reduce the dramatic size differences
        normalized = (game_count - min_games) / (max_games - min_games)
        scaled = min_size + (max_size - min_size) * (normalized**0.5)
        return scaled

    # Function to scale emoji text size
    def scale_emoji_size(game_count):
        if max_games == min_games:
            return 25
        normalized = (game_count - min_games) / (max_games - min_games)
        return int(20 + (40 - 20) * (normalized**0.5))  # Scale from 20 to 40

    # Group data by player for a cleaner legend
    for player_name in player_agent_pool.name.unique():
        player_df = player_agent_pool[player_agent_pool["name"] == player_name]

        # Add a trace for each player (bubbles)
        fig.add_trace(
            go.Scatter(
                x=player_df[x_stat],
                y=player_df[y_stat],
                mode="markers",
                marker=dict(
                    symbol="circle",
                    size=[scale_bubble_size(games) for games in player_df["game_id"]],
                    color=color_map[player_name],
                    opacity=0.7,  # Make circles slightly transparent so agent emojis show better
                ),
                name=player_name,  # The name for the legend
                legendgroup=player_name,  # Group for legend interactions
                customdata=player_df[["agent", "game_id", "name"]],
                hovertemplate="<br>".join(
                    [
                        "<b>Player</b>: %{customdata[2]}",
                        "<b>Agent</b>: %{customdata[0]}",
                        "<b>Games Played</b>: %{customdata[1]}",
                        "<b>" + x_stat + "</b>: %{x}",
                        "<b>" + y_stat + "</b>: %{y}",
                        "<extra></extra>",  # This removes the trace name box
                    ]
                ),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=player_df[x_stat],
                y=player_df[y_stat],
                mode="text",
                text=player_df["agent_emoji"],
                textfont=dict(
                    size=[scale_emoji_size(games) for games in player_df["game_id"]],
                    color="black",
                ),
                textposition="middle center",
                name=f"{player_name}_emojis",
                legendgroup=player_name,  # Same group - will hide/show together
                showlegend=False,  # Don't show separate legend entry
                customdata=player_df[["agent", "game_id", "name"]],
                hovertemplate="<br>".join(
                    [
                        "<b>Player</b>: %{customdata[2]}",
                        "<b>Agent</b>: %{customdata[0]}",
                        "<b>Games Played</b>: %{customdata[1]}",
                        "<b>" + x_stat + "</b>: %{x}",
                        "<b>" + y_stat + "</b>: %{y}",
                        "<extra></extra>",
                    ]
                ),
            )
        )

    fig.update_layout(
        xaxis_title=x_stat,
        yaxis_title=y_stat,
        legend_title_text="Player",
        font=dict(family="Arial, sans-serif", size=12, color="#333"),
        title_font_size=20,
    )

    return fig
