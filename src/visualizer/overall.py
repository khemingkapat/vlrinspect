import plotly.express as px
from plotly.graph_objects import Figure
import pandas as pd


def plot_team_win_lose(df: pd.DataFrame) -> Figure:
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


def plot_player_stats(df, sort_by="total", sort_order="desc") -> Figure:
    """
    Plot player stats with sorting options

    Parameters:
    - sort_by: 'total' (sum of atk+def), 'atk', 'def', or 'alphabetical'
    - sort_order: 'desc' (descending) or 'asc' (ascending)
    """
    stats_columns = [
        col
        for col in df.columns
        if col not in ["name", "cat"] and df[col].dtype in ["float64", "int64"]
    ]
    initial_stat = stats_columns[0]

    if "atk" in df["cat"].values and "def" in df["cat"].values:
        color_map = {"atk": "#FF6B6B", "def": "#4ECDC4"}
        categories = ["atk", "def"]
    else:
        color_map = {"lose": "#FF6B6B", "win": "#4ECDC4"}
        categories = ["lose", "win"]

    def sort_players_by_stat(df, stat, sort_by, sort_order):
        """Sort players based on the specified criteria"""
        if sort_by == "alphabetical":
            player_order = sorted(df["name"].unique())
        else:
            # Create pivot table for easier sorting
            pivot_df = df.pivot(index="name", columns="cat", values=stat).fillna(0)

            if sort_by == "total":
                # Sort by sum of both categories
                sort_values = pivot_df.sum(axis=1)
            elif sort_by in pivot_df.columns:
                # Sort by specific category (atk or def)
                sort_values = pivot_df[sort_by]
            else:
                # Default to total if category not found
                sort_values = pivot_df.sum(axis=1)

            ascending = sort_order == "asc"
            player_order = sort_values.sort_values(ascending=ascending).index.tolist()

        return player_order

    # Sort the dataframe for initial display
    initial_order = sort_players_by_stat(df, initial_stat, sort_by, sort_order)
    df_sorted = df.copy()
    df_sorted["name"] = pd.Categorical(
        df_sorted["name"], categories=initial_order, ordered=True
    )
    df_sorted = df_sorted.sort_values("name")

    fig = px.bar(
        df_sorted,
        x="name",
        y=initial_stat,
        color="cat",
        barmode="group",
        title=f"Player Comparison - {initial_stat} (sorted by {sort_by})",
        labels={"name": "Player", "cat": "Category"},
        color_discrete_map=color_map,
    )

    # Create dropdown buttons for each stat
    dropdown_buttons = []
    for stat in stats_columns:
        # Sort players for this stat
        player_order = sort_players_by_stat(df, stat, sort_by, sort_order)

        # Prepare sorted data for each category
        y_data = []
        for cat in categories:
            cat_data = df[df["cat"] == cat].set_index("name")
            y_values = [
                cat_data.loc[player, stat] if player in cat_data.index else 0
                for player in player_order
            ]
            y_data.append(y_values)

        dropdown_buttons.append(
            dict(
                label=stat,
                method="update",
                args=[
                    {
                        "y": y_data,
                        "x": [player_order, player_order],  # Update x-axis order too
                        "marker.color": [color_map[cat] for cat in categories],
                    },
                    {
                        "title": f"Player Comparison - {stat} (sorted by {sort_by})",
                        "yaxis.title": stat,
                    },
                ],
            )
        )

    # Add dropdown menu
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=dropdown_buttons,
                direction="down",
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top",
            ),
        ],
        annotations=[
            dict(
                text="Select Stat:",
                x=0,
                xref="paper",
                y=1.15,
                yref="paper",
                align="left",
                showarrow=False,
                font=dict(size=14),
            )
        ],
        height=600,
        margin=dict(t=100),
    )
    return fig
