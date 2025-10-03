import streamlit as st
from src.visualizer import Visualizer
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def map_page():
    team_1_name = st.session_state.team_histories["team1"]["name"]
    team_2_name = st.session_state.team_histories["team2"]["name"]
    team_1_history = st.session_state.team_histories["team1"]["history"]
    team_2_history = st.session_state.team_histories["team2"]["history"]

    # Create individual figures
    team_1_pick_ban = Visualizer.plot_team_pick_ban(team_1_history)
    team_2_pick_ban = Visualizer.plot_team_pick_ban(team_2_history)
    team_1_map_agent = Visualizer.plot_players_map_agent_pool(team_1_history)
    team_2_map_agent = Visualizer.plot_players_map_agent_pool(team_2_history)
    team_1_side_bias = Visualizer.plot_team_side_bias(team_1_history)
    team_2_side_bias = Visualizer.plot_team_side_bias(team_2_history)
    team_1_pistol_impact = Visualizer.plot_map_pistol_impact(team_1_history)
    team_2_pistol_impact = Visualizer.plot_map_pistol_impact(team_2_history)

    fig = make_subplots(
        rows=3,
        cols=4,
        specs=[
            # Row 1: Side Bias and Map Agent for both teams
            [{"type": "xy"}, {"type": "domain"}, {"type": "domain"}, {"type": "xy"}],
            # Row 2: Pick/Ban charts (2 cols each)
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            # Row 3: Pistol Impact charts (2 cols each)
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
        ],
        subplot_titles=(
            f"{team_1_name}'s Side Bias",
            f"{team_1_name}'s Agent Pool",
            f"{team_2_name}'s Agent Pool",
            f"{team_2_name}'s Side Bias",
            f"{team_1_name}'s Pick and Ban",
            f"{team_2_name}'s Pick and Ban",
            f"{team_1_name}'s Pistol Impact",
            f"{team_2_name}'s Pistol Impact",
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
        row_heights=[0.6, 0.2, 0.2],
        column_widths=[0.05, 0.45, 0.45, 0.05],
    )

    # ============ ROW 1: SIDE BIAS & MAP AGENT ============

    # Row 1, Col 1: Team 1 Side Bias (Heatmap)
    for trace in team_1_side_bias.data:
        new_trace = go.Heatmap(trace)
        new_trace.showscale = False  # Remove color bar
        new_trace.colorscale = "Viridis"  # Ensure Viridis colormap
        fig.add_trace(new_trace, row=1, col=1)

    # Row 1, Col 2: Team 1 Map Agent (Sankey)
    for trace in team_1_map_agent.data:
        new_trace = go.Sankey(trace)
        new_trace.domain = None  # Remove domain to let subplot handle it
        fig.add_trace(new_trace, row=1, col=2)

    # Row 1, Col 3: Team 2 Map Agent (Sankey - MIRRORED)
    for trace in team_2_map_agent.data:
        new_trace = go.Sankey()

        # Mirror the Sankey by swapping source and target
        new_trace.node = dict(
            pad=trace.node.pad,
            thickness=trace.node.thickness,
            line=trace.node.line,
            label=trace.node.label,
            color=trace.node.color,
        )

        new_trace.link = dict(
            # Swap source and target to mirror
            source=trace.link.target,
            target=trace.link.source,
            value=trace.link.value,
            color=trace.link.color,
            customdata=trace.link.customdata,
            hovertemplate=trace.link.hovertemplate,
        )

        new_trace.domain = None
        fig.add_trace(new_trace, row=1, col=3)

    # Row 1, Col 4: Team 2 Side Bias (Heatmap)
    for trace in team_2_side_bias.data:
        new_trace = go.Heatmap(trace)
        new_trace.showscale = False  # Remove color bar
        new_trace.colorscale = "Viridis"  # Ensure Viridis colormap
        fig.add_trace(new_trace, row=1, col=4)

    # ============ ROW 2: PICK/BAN (NO MIRRORING) ============

    # Team 1 Pick/Ban
    for trace in team_1_pick_ban.data:
        new_trace = go.Scatter(trace) if trace.mode else trace
        new_trace.showlegend = False
        fig.add_trace(new_trace, row=2, col=1)

    # Team 2 Pick/Ban (same orientation as Team 1)
    for i, trace in enumerate(team_2_pick_ban.data):
        new_trace = go.Scatter(trace) if trace.mode else trace
        # Show legend only for team 2
        new_trace.showlegend = trace.mode == "markers"
        if trace.mode == "markers":
            new_trace.legendgroup = trace.name
        fig.add_trace(new_trace, row=2, col=3)

    # ============ ROW 3: PISTOL IMPACT ============

    # Team 1 Pistol Impact
    for trace in team_1_pistol_impact.data:
        new_trace = go.Bar(trace)
        new_trace.showlegend = False
        fig.add_trace(new_trace, row=3, col=1)

    # Team 2 Pistol Impact
    for trace in team_2_pistol_impact.data:
        new_trace = go.Bar(trace)
        new_trace.showlegend = True
        new_trace.legendgroup = trace.name
        fig.add_trace(new_trace, row=3, col=3)

    # ============ UPDATE AXES ============

    # Row 1 - Side Bias Heatmaps
    fig.update_xaxes(title_text="Side", row=1, col=1)
    fig.update_yaxes(title_text="Map", row=1, col=1)
    fig.update_xaxes(title_text="Side", row=1, col=4)
    fig.update_yaxes(title_text="Map", row=1, col=4)

    # Row 2 - Pick/Ban Charts
    # Calculate axis limits for symmetry
    max_pick_1 = max(
        [
            abs(y)
            for trace in team_1_pick_ban.data
            if trace.mode == "markers"
            for y in trace.y
        ]
    )
    max_pick_2 = max(
        [
            abs(y)
            for trace in team_2_pick_ban.data
            if trace.mode == "markers"
            for y in trace.y
        ]
    )
    max_val = max(max_pick_1, max_pick_2)
    axis_limit = max_val + (max_val * 0.1)

    tick_interval = max(1, int(axis_limit / 5))
    tick_vals = list(range(-int(axis_limit), int(axis_limit) + 1, tick_interval))
    tick_labels = [str(abs(val)) for val in tick_vals]

    # Team 1 Pick/Ban axes
    fig.update_xaxes(title_text="Map", row=2, col=1)
    fig.update_yaxes(
        title_text="Count",
        row=2,
        col=1,
        tickvals=tick_vals,
        ticktext=tick_labels,
        range=[-axis_limit, axis_limit],
        zeroline=True,
        zerolinecolor="#666666",
        zerolinewidth=2,
        gridcolor="#F0F0F0",
        showgrid=True,
    )

    # Team 2 Pick/Ban axes
    fig.update_xaxes(title_text="Map", row=2, col=3)
    fig.update_yaxes(
        title_text="Count",
        row=2,
        col=3,
        tickvals=tick_vals,
        ticktext=tick_labels,
        range=[-axis_limit, axis_limit],
        zeroline=True,
        zerolinecolor="#666666",
        zerolinewidth=2,
        gridcolor="#F0F0F0",
        showgrid=True,
    )

    # Row 3 - Pistol Impact
    fig.update_xaxes(title_text="Map", row=3, col=1)
    fig.update_yaxes(title_text="Win Probability", row=3, col=1, tickformat=".0%")
    fig.update_xaxes(title_text="Map", row=3, col=3)
    fig.update_yaxes(title_text="Win Probability", row=3, col=3, tickformat=".0%")

    # ============ OVERALL LAYOUT ============
    fig.update_layout(
        height=900,
        showlegend=True,
        title_text=f"Map Analysis: {team_1_name} vs {team_2_name}",
        title_x=0.4,
        title_font_size=24,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.65,
            xanchor="left",
            x=1.01,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
        ),
    )

    fig.update_layout(coloraxis_showscale=False)

    # Remove background from all subplots
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

    # Re-enable grid only for pick/ban charts
    fig.update_yaxes(showgrid=True, gridcolor="#F0F0F0", row=2, col=1)
    fig.update_yaxes(showgrid=True, gridcolor="#F0F0F0", row=2, col=3)

    st.plotly_chart(fig, use_container_width=True)
