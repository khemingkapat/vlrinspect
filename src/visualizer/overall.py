import plotly.express as px
from plotly.graph_objects import Figure
import pandas as pd


def plot_team_win_lose(df: pd.DataFrame) -> Figure:
    fig = px.pie(
        df,
        names="outcome",
        values="count",
        title="Team Win/Loss Ratio",
        hole=0.4,  # Use this to create a donut chart
        color="outcome",
        color_discrete_map={"win": "green", "lose": "red"},
    )
    return fig
