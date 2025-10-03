import streamlit as st
from src.visualizer import Visualizer
from plotly.subplots import make_subplots


def overview_page():
    team_1_name = st.session_state.team_histories["team1"]["name"]
    team_2_name = st.session_state.team_histories["team2"]["name"]
    team_1_history = st.session_state.team_histories["team1"]["history"]
    team_2_history = st.session_state.team_histories["team2"]["history"]

    # Create custom layout matching your screenshot:
    # Row 1: Pistol (small) | Win/Loss (large) | Win/Loss (large) | Pistol (small)
    # Row 2: Buy Type (full width left) | Buy Type (full width right)
    # Row 3: Win Condition (full width left) | Win Condition (full width right)

    fig = make_subplots(
        rows=3,
        cols=4,
        specs=[
            # Row 1: Pistol charts (1 col each) and Win/Loss pies (1 col each in the middle)
            [{"type": "xy"}, {"type": "domain"}, {"type": "domain"}, {"type": "xy"}],
            # Row 2: Buy Type charts (2 cols each)
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            # Row 3: Win Condition charts (2 cols each)
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
        ],
        subplot_titles=(
            f"{team_1_name}'s Pistol Impact",
            f"{team_1_name}'s Win/Loss Ratio",
            "",  # Empty for reversed pistol position
            f"{team_2_name}'s Pistol Impact",
            f"{team_1_name}'s Win/Lose Probabilities by Buy Type",
            f"{team_2_name}'s Win/Lose Probabilities by Buy Type",
            f"{team_1_name}'s Win/Lose Probabilities by Win Condition",
            f"{team_2_name}'s Win/Lose Probabilities by Win Condition",
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.06,
        row_heights=[0.35, 0.32, 0.33],
        column_widths=[0.15, 0.35, 0.35, 0.15],
    )

    # ========== ROW 1, COL 1: Team 1 Pistol Impact ==========
    pistol_fig_1 = Visualizer.plot_team_pistol_impact(team_1_history)
    for trace in pistol_fig_1.data:
        trace.showlegend = False
        fig.add_trace(trace, row=1, col=1)

    # ========== ROW 1, COL 2: Team 1 Win/Loss Pie ==========
    winloss_fig_1 = Visualizer.plot_team_win_lose(team_1_history)
    for trace in winloss_fig_1.data:
        # trace.showlegend = True
        # trace.legendgroup = "wl"
        fig.add_trace(trace, row=1, col=2)

    # ========== ROW 1, COL 3: Team 2 Win/Loss Pie ==========
    winloss_fig_2 = Visualizer.plot_team_win_lose(team_2_history)
    for trace in winloss_fig_2.data:
        # trace.showlegend = False  # Avoid duplicate legend
        # trace.legendgroup = "wl"
        fig.add_trace(trace, row=1, col=3)

    # ========== ROW 1, COL 4: Team 2 Pistol Impact (Reversed) ==========
    pistol_fig_2 = Visualizer.plot_team_pistol_impact(team_2_history)
    for trace in pistol_fig_2.data:
        trace.showlegend = False
        trace.textposition = "outside"  # Add this line to fix annotation position
        fig.add_trace(trace, row=1, col=4)

    # ========== ROW 2, COL 1-2: Team 1 Buy Type ==========
    buytype_fig_1 = Visualizer.plot_team_buy_type_win_lose(team_1_history)
    for trace in buytype_fig_1.data:
        trace.showlegend = True
        trace.legendgroup = "result"
        fig.add_trace(trace, row=2, col=1)

    # ========== ROW 2, COL 3-4: Team 2 Buy Type ==========
    buytype_fig_2 = Visualizer.plot_team_buy_type_win_lose(team_2_history)
    for trace in buytype_fig_2.data:
        trace.showlegend = False  # Avoid duplicate legend
        trace.legendgroup = "result"
        fig.add_trace(trace, row=2, col=3)

    # ========== ROW 3, COL 1-2: Team 1 Win Condition ==========
    wincond_fig_1 = Visualizer.plot_team_win_condition(team_1_history)
    for trace in wincond_fig_1.data:
        trace.showlegend = False
        fig.add_trace(trace, row=3, col=1)

    # ========== ROW 3, COL 3-4: Team 2 Win Condition ==========
    wincond_fig_2 = Visualizer.plot_team_win_condition(team_2_history)
    for trace in wincond_fig_2.data:
        trace.showlegend = False
        fig.add_trace(trace, row=3, col=3)

    # ========== Update Axes ==========
    # Pistol charts
    fig.update_xaxes(row=1, col=1)
    fig.update_yaxes(row=1, col=1)
    fig.update_xaxes(autorange="reversed", row=1, col=4)
    fig.update_yaxes(row=1, col=4, side="right")

    # Buy Type charts
    fig.update_xaxes(tickangle=45, row=2, col=1)
    fig.update_yaxes(tickformat=".0%", row=2, col=1)
    fig.update_xaxes(tickangle=45, row=2, col=3)
    fig.update_yaxes(tickformat=".0%", row=2, col=3)

    # Win Condition charts
    fig.update_xaxes(row=3, col=1)
    fig.update_yaxes(row=3, col=1)
    fig.update_xaxes(row=3, col=3)
    fig.update_yaxes(row=3, col=3)

    # ========== Global Layout ==========
    fig.update_layout(
        height=900,  # Fits standard desktop screen (1080p)
        showlegend=True,
        title_text=f"Match Analysis Overview: {team_1_name} vs {team_2_name}",
        title_x=0.4,
        title_font_size=20,
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="closest",
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5
        ),
        barmode="stack",
    )

    # Remove all subplot titles since each chart has its own title
    # fig.for_each_annotation(lambda a: a.update(text=""))

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "scrollZoom": True,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        },
    )
