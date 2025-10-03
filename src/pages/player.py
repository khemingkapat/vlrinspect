import streamlit as st
from plotly.subplots import make_subplots
from visualizer import Visualizer
from utils import stat_cols_full


def player_page():
    team_1_name = st.session_state.team_histories["team1"]["name"]
    team_2_name = st.session_state.team_histories["team2"]["name"]
    team_1_history = st.session_state.team_histories["team1"]["history"]
    team_2_history = st.session_state.team_histories["team2"]["history"]

    _, stat_box, cat_box = st.columns([8, 1, 1])

    with stat_box:
        stat_col = st.selectbox("Stat Show", tuple(stat_cols_full))

    with cat_box:
        cat_by = st.selectbox("Categorized By", ("side", "win"))

    # Create individual figures
    t1_agent_pool = Visualizer.plot_players_agent_pool(team_1_history)
    t2_agent_pool = Visualizer.plot_players_agent_pool(team_2_history)
    t1_stat_history = Visualizer.plot_player_stat_history(
        team_1_history, stat_column=stat_col
    )
    t2_stat_history = Visualizer.plot_player_stat_history(
        team_2_history, stat_column=stat_col
    )
    t1_player_stats = Visualizer.plot_player_stats(
        team_1_history, stat_column=stat_col, category_type=cat_by
    )
    t2_player_stats = Visualizer.plot_player_stats(
        team_2_history, stat_column=stat_col, category_type=cat_by
    )

    fig = make_subplots(
        rows=2,
        cols=4,
        specs=[
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "xy"}, {"type": "polar"}, {"type": "polar"}, {"type": "xy"}],
        ],
        subplot_titles=(
            f"{team_1_name}'s Player Agent Pool",
            f"{team_2_name}'s Player Agent Pool",
            f"{team_1_name}'s Player Stat History",
            f"{team_1_name}'s Player Stat",
            f"{team_2_name}'s Player Stat",
            f"{team_2_name}'s Player Stat History",
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.10,
        row_heights=[0.6, 0.4],
        column_widths=[0.35, 0.15, 0.15, 0.35],
    )

    # Add Row 1: Agent Pool
    for trace in t1_agent_pool.data:
        fig.add_trace(trace, row=1, col=1)
    for trace in t2_agent_pool.data:
        fig.add_trace(trace, row=1, col=3)

    # Add Row 2: Stat History & Player Stats
    for trace in t1_stat_history.data:
        fig.add_trace(trace, row=2, col=1)
    for trace in t2_stat_history.data:
        fig.add_trace(trace, row=2, col=4)
    for trace in t1_player_stats.data:
        fig.add_trace(trace, row=2, col=2)
    for trace in t2_player_stats.data:
        fig.add_trace(trace, row=2, col=3)

    # Update layout
    fig.update_layout(
        height=850,
        showlegend=True,
        title_text="Player Statistics Comparison",
        title_x=0.4,
    )

    # Update axes labels (fixed rows/cols)
    fig.update_xaxes(title_text="Game Sequence", row=2, col=1)
    fig.update_xaxes(title_text="Game Sequence", row=2, col=4)

    st.plotly_chart(fig, use_container_width=True)
