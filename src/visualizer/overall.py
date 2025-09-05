from re import Match
import plotly.express as px
from plotly.graph_objects import Figure
import pandas as pd
from models import MatchHistory
from .logic.overall import (
    get_team_buy_type_win_lose,
    get_team_win_condition,
    get_team_win_lose,
    get_player_stats,
)


def plot_team_win_lose(matches: MatchHistory) -> Figure:
    df = get_team_win_lose(matches)
    fig = px.pie(
        df,
        names="outcome",
        values="count",
        title="Team Win/Loss Ratio",
        hole=0.4,
        color="outcome",
        color_discrete_map={"win": "green", "lose": "red"},
    )
    return fig


def plot_player_stats(
    matches: "MatchHistory",
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


# def plot_player_stats(
#     matches: MatchHistory, sort_by="mean", sort_order="desc"
# ) -> Figure:
#     side_df = get_player_stats(matches, cat_by="side")
#     win_df = get_player_stats(matches, cat_by="win")
#
#     df = side_df
#
#     stats_columns = [
#         col
#         for col in df.columns
#         if col not in ["name", "cat"] and df[col].dtype in ["float64", "int64"]
#     ]
#     initial_stat = stats_columns[0]
#
#     def get_color_map_and_categories(df):
#         if "atk" in df["cat"].values and "def" in df["cat"].values:
#             color_map = {"atk": "#FF6B6B", "def": "#4ECDC4"}
#             categories = ["atk", "def"]
#         else:
#             color_map = {"lose": "#FF6B6B", "win": "#4ECDC4"}
#             categories = ["lose", "win"]
#         return color_map, categories
#
#     def sort_players_by_stat(df, stat, sort_by, sort_order):
#         """Sort players based on the specified criteria"""
#         if sort_by == "alphabetical":
#             player_order = sorted(df["name"].unique())
#         else:
#             # Create pivot table for easier sorting
#             pivot_df = df.pivot(index="name", columns="cat", values=stat).fillna(0)
#
#             if sort_by == "mean":
#                 sort_values = pivot_df.mean(axis=1)
#             elif sort_by in pivot_df.columns:
#                 # Sort by specific category
#                 sort_values = pivot_df[sort_by]
#             else:
#                 # Default to mean if category not found
#                 sort_values = pivot_df.mean(axis=1)
#
#             ascending = sort_order == "asc"
#             player_order = sort_values.sort_values(ascending=ascending).index.tolist()
#
#         return player_order
#
#     color_map, categories = get_color_map_and_categories(df)
#     initial_order = sort_players_by_stat(df, initial_stat, sort_by, sort_order)
#     df_sorted = df.copy()
#     df_sorted["name"] = pd.Categorical(
#         df_sorted["name"], categories=initial_order, ordered=True
#     )
#     df_sorted = df_sorted.sort_values("name")
#
#     fig = px.bar(
#         df_sorted,
#         x="name",
#         y=initial_stat,
#         color="cat",
#         barmode="group",
#         title=f"Player Comparison - {initial_stat} (Side, sorted by {sort_by})",
#         labels={"name": "Player", "cat": "Category"},
#         color_discrete_map=color_map,
#         hover_data={"name": True, "cat": True, initial_stat: ":.2f"},
#     )
#
#     # Create stat dropdown buttons for a given dataframe
#     def create_stat_buttons(df, cat_label):
#         color_map, categories = get_color_map_and_categories(df)
#         buttons = []
#
#         for stat in stats_columns:
#             player_order = sort_players_by_stat(df, stat, sort_by, sort_order)
#             y_data = []
#             for cat in categories:
#                 cat_data = df[df["cat"] == cat].set_index("name")
#                 y_values = [
#                     cat_data.loc[player, stat] if player in cat_data.index else 0
#                     for player in player_order
#                 ]
#                 y_data.append(y_values)
#
#             # Tooltip template for this stat
#             tpl = f"Category: %{{fullData.name}}<br>Player: %{{x}}<br>{stat}: %{{y:.2f}}<extra></extra>"
#
#             buttons.append(
#                 dict(
#                     label=stat,
#                     method="update",
#                     args=[
#                         {
#                             "y": y_data,
#                             "x": [player_order, player_order],
#                             "marker.color": [color_map[cat] for cat in categories],
#                             "name": categories,  # trace names = categories
#                             "hovertemplate": [tpl] * len(categories),
#                         },
#                         {
#                             "title": {
#                                 "text": f"Player Comparison - {stat} ({cat_label}, sorted by {sort_by})"
#                             },
#                             "yaxis": {"title": {"text": stat}},
#                             "xaxis": {
#                                 "title": {"text": "Player"}
#                             },  # optional, keeps x label consistent
#                         },
#                     ],
#                 )
#             )
#         return buttons
#
#     def create_category_buttons():
#         side_color_map, side_categories = get_color_map_and_categories(side_df)
#         win_color_map, win_categories = get_color_map_and_categories(win_df)
#
#         # Precompute y-data for Side
#         side_order = sort_players_by_stat(side_df, initial_stat, sort_by, sort_order)
#         side_y_data = []
#         for cat in side_categories:
#             cat_data = side_df[side_df["cat"] == cat].set_index("name")
#             y_values = [
#                 cat_data.loc[player, initial_stat] if player in cat_data.index else 0
#                 for player in side_order
#             ]
#             side_y_data.append(y_values)
#
#         # Precompute y-data for Win/Lose
#         win_order = sort_players_by_stat(win_df, initial_stat, sort_by, sort_order)
#         win_y_data = []
#         for cat in win_categories:
#             cat_data = win_df[win_df["cat"] == cat].set_index("name")
#             y_values = [
#                 cat_data.loc[player, initial_stat] if player in cat_data.index else 0
#                 for player in win_order
#             ]
#             win_y_data.append(y_values)
#
#         # Tooltip templates
#         side_tpl = f"Category: %{{fullData.name}}<br>Player: %{{x}}<br>{initial_stat}: %{{y:.2f}}<extra></extra>"
#         win_tpl = f"Category: %{{fullData.name}}<br>Player: %{{x}}<br>{initial_stat}: %{{y:.2f}}<extra></extra>"
#
#         return [
#             dict(
#                 label="Side",
#                 method="update",
#                 args=[
#                     {
#                         "y": side_y_data,
#                         "x": [side_order, side_order],
#                         "marker.color": [
#                             side_color_map[cat] for cat in side_categories
#                         ],
#                         "name": side_categories,
#                         "hovertemplate": [side_tpl] * len(side_categories),
#                     },
#                     {
#                         "title": f"Player Comparison - {initial_stat} (Side, sorted by {sort_by})"
#                     },
#                 ],
#             ),
#             dict(
#                 label="Win/Lose",
#                 method="update",
#                 args=[
#                     {
#                         "y": win_y_data,
#                         "x": [win_order, win_order],
#                         "marker.color": [win_color_map[cat] for cat in win_categories],
#                         "name": win_categories,
#                         "hovertemplate": [win_tpl] * len(win_categories),
#                     },
#                     {
#                         "title": {
#                             "text": f"Player Comparison - {initial_stat} (Win/Lose, sorted by {sort_by})"
#                         },
#                         "yaxis": {"title": {"text": initial_stat}},
#                         "xaxis": {"title": {"text": "Player"}},
#                     },
#                 ],
#             ),
#         ]
#
#     # Create all buttons
#     side_stat_buttons = create_stat_buttons(side_df, "Side")
#     category_buttons = create_category_buttons()
#
#     # Add both dropdown menus
#     fig.update_layout(
#         updatemenus=[
#             # Category selector
#             dict(
#                 buttons=category_buttons,
#                 direction="down",
#                 showactive=True,
#                 x=0.15,
#                 xanchor="left",
#                 y=1.12,
#                 yanchor="top",
#             ),
#             # Stat selector (starts with side buttons)
#             dict(
#                 buttons=side_stat_buttons,
#                 direction="down",
#                 showactive=True,
#                 x=0.45,
#                 xanchor="left",
#                 y=1.12,
#                 yanchor="top",
#             ),
#         ],
#         annotations=[
#             dict(
#                 text="Category:",
#                 x=0.02,
#                 xref="paper",
#                 y=1.12,
#                 yref="paper",
#                 align="left",
#                 showarrow=False,
#                 font=dict(size=14),
#             ),
#             dict(
#                 text="Select Stat:",
#                 x=0.32,
#                 xref="paper",
#                 y=1.12,
#                 yref="paper",
#                 align="left",
#                 showarrow=False,
#                 font=dict(size=14),
#             ),
#         ],
#         height=600,
#         margin=dict(t=150),
#     )
#
#     return fig


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
    df = get_team_win_condition(matches).reset_index()
    df_melted = df.melt(id_vars="reason", var_name="result", value_name="count")

    fig = px.bar(
        df_melted,
        x="reason",
        y="count",
        color="result",
        barmode="group",
        title=f"{matches.full_name}'s Win/Loss Reasons",
        labels={"reason": "Reason", "count": "Number of Rounds", "result": "Result"},
        color_discrete_map={"win": "#4ECDC4", "lose": "#FF6B6B"},
    )

    fig.update_layout(
        xaxis_title="Reason",
        yaxis_title="Number of Rounds",
        legend_title_text="Result",
        font=dict(family="Arial, sans-serif", size=12, color="#333"),
    )

    return fig
