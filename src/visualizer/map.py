from src.models.match_history import MatchHistory
from .logic.map import (
    get_players_map_agent_pool,
    get_team_pick_ban,
    get_team_side_bias,
    get_map_pistol_impact,
)
from plotly.graph_objects import Figure
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


def plot_team_pick_ban(matches: MatchHistory) -> Figure:
    team_pick_ban = get_team_pick_ban(matches).reset_index()

    # Create figure
    fig = go.Figure()

    # Add connecting lines between pick and ban markers (bans as negative)
    for _, row in team_pick_ban.iterrows():
        fig.add_trace(
            go.Scatter(
                y=[row["pick"], -row["ban"]],
                x=[row["map"], row["map"]],
                mode="lines",
                line=dict(color="#E0E0E0", width=2),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Add pick markers (positive side - top)
    fig.add_trace(
        go.Scatter(
            y=team_pick_ban["pick"],
            x=team_pick_ban["map"],
            mode="markers",
            name="Pick",
            marker=dict(size=14, color="#4ECDC4", line=dict(color="#3DB8B0", width=2)),
            hovertemplate="<b>%{x}</b><br>Picks: %{y}<extra></extra>",
        )
    )

    # Add ban markers (negative side - bottom, but show positive values in hover)
    fig.add_trace(
        go.Scatter(
            y=-team_pick_ban["ban"],
            x=team_pick_ban["map"],
            mode="markers",
            name="Ban",
            marker=dict(size=14, color="#FF6B6B", line=dict(color="#E85555", width=2)),
            customdata=team_pick_ban["ban"],
            hovertemplate="<b>%{x}</b><br>Bans: %{customdata}<extra></extra>",
        )
    )

    # Calculate max value for symmetric axis
    max_pick = team_pick_ban["pick"].max()
    max_ban = team_pick_ban["ban"].max()
    max_val = max(max_pick, max_ban)
    axis_limit = max_val + (max_val * 0.1)  # Add 10% padding

    # Create custom tick values and labels (showing positive numbers on both sides)
    tick_interval = max(1, int(axis_limit / 5))
    tick_vals = list(range(-int(axis_limit), int(axis_limit) + 1, tick_interval))
    tick_labels = [str(abs(val)) for val in tick_vals]

    # Update layout
    fig.update_layout(
        title=f"{matches.full_name}'s Pick and Ban Counts by Map",
        yaxis_title="Count",
        xaxis_title="Map",
        hovermode="closest",
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F0F0F0",
            zeroline=True,
            zerolinecolor="#666666",
            zerolinewidth=2,
            tickvals=tick_vals,
            ticktext=tick_labels,
            range=[-axis_limit, axis_limit],
        ),
        xaxis=dict(showgrid=False),
        margin=dict(l=80, r=50, t=80, b=100),
        # Add annotations to label the sides
        annotations=[
            dict(
                y=axis_limit * 0.7,
                x=0.5,
                xref="paper",
                yref="y",
                text="Picks ↑",
                showarrow=False,
                font=dict(size=12, color="#4ECDC4"),
                textangle=0,
            ),
            dict(
                y=-axis_limit * 0.7,
                x=0.5,
                xref="paper",
                yref="y",
                text="↓ Bans",
                showarrow=False,
                font=dict(size=12, color="#FF6B6B"),
                textangle=0,
            ),
        ],
    )

    return fig


def plot_team_side_bias(matches: MatchHistory) -> Figure:

    # Get the side bias data
    team_side_win = get_team_side_bias(matches).reset_index()

    # Pivot the data to have maps as rows and sides as columns
    heatmap_data = team_side_win.pivot(
        index="map", columns="team_side", values="win_rate"
    )

    heatmap_data = heatmap_data.loc[heatmap_data.mean(axis=1).sort_values().index]

    # Create the heatmap
    fig = px.imshow(
        heatmap_data,
        text_auto=".2f",
        aspect="auto",  # vertical layout
        color_continuous_scale="Viridis",
        labels={"x": "Side", "y": "Map", "color": "Win Rate (%)"},
        title=f"{matches.full_name}'s Side Bias",
    )

    # Reverse Y axis so top map appears at top
    fig.update_yaxes(autorange="reversed")

    return fig


def plot_map_pistol_impact(matches: MatchHistory) -> Figure:
    map_pistol_impact = get_map_pistol_impact(matches)

    map_pistol_prob = (
        map_pistol_impact.xs("prob", level="type")
        .sort_values("pistol", ascending=False)
        .reset_index()
    )

    map_pistol_total = (
        map_pistol_impact.xs("total", level="type")
        .reindex(map_pistol_prob["map_name"])
        .reset_index()
    )

    map_pistol_wins = (
        map_pistol_impact.xs("win", level="type")
        .reindex(map_pistol_prob["map_name"])
        .reset_index()
    )

    df_melted = pd.melt(
        map_pistol_prob,
        id_vars=["map_name"],
        value_vars=["pistol", "second_round", "2_round"],
        var_name="round_type",
        value_name="win_probability",
    )

    df_total_melted = pd.melt(
        map_pistol_total,
        id_vars=["map_name"],
        value_vars=["pistol", "second_round", "2_round"],
        var_name="round_type",
        value_name="total_rounds",
    )

    df_wins_melted = pd.melt(
        map_pistol_wins,
        id_vars=["map_name"],
        value_vars=["pistol", "second_round", "2_round"],
        var_name="round_type",
        value_name="rounds_won",
    )

    df_combined = df_melted.merge(df_total_melted, on=["map_name", "round_type"]).merge(
        df_wins_melted, on=["map_name", "round_type"]
    )

    fig = px.bar(
        df_combined,
        x="map_name",
        y="win_probability",
        color="round_type",
        barmode="group",
        title=f"{matches.full_name}'s Pistol Impact by Map",
        labels={
            "map_name": "Map Name",
            "win_probability": "Win Probability",
            "round_type": "Round Type",
        },
        color_discrete_map={
            "pistol": "#FF6B6B",
            "second_round": "#4ECDC4",
            "2_round": "#45B7D1",
        },
        hover_data={
            "total_rounds": True,
            "rounds_won": True,
            "win_probability": ":.1%",  # Format as percentage
        },
        custom_data=["total_rounds", "rounds_won"],
    )

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>"
        + "Round Type: %{fullData.name}<br>"
        + "Win Rate: %{y:.1%}<br>"
        + "Rounds Won: %{customdata[1]:.0f}<br>"
        + "Total Rounds: %{customdata[0]:.0f}<br>"
        + "<extra></extra>"
    )

    return fig


def plot_players_map_agent_pool(matches: MatchHistory):
    players_map_agent_pool = get_players_map_agent_pool(matches)[
        ["game_id"]
    ].reset_index()

    # Create a more focused view on agent preferences
    players = sorted(players_map_agent_pool["name"].unique())
    agents = sorted(players_map_agent_pool["agent"].unique())

    # Enhanced labels with pick statistics
    player_stats = (
        players_map_agent_pool.groupby("name")
        .agg({"game_id": ["sum", "count"], "agent": "nunique", "map": "nunique"})
        .round(1)
    )

    player_labels = []
    for p in players:
        total_picks = player_stats.loc[p, ("game_id", "sum")]
        unique_agents = player_stats.loc[p, ("agent", "nunique")]
        player_labels.append(f"{p}\n{total_picks} picks\n{unique_agents} agents")

    agent_stats = players_map_agent_pool.groupby("agent").agg(
        {"game_id": "sum", "name": "nunique"}
    )

    agent_labels = []
    for a in agents:
        total_picks = agent_stats.loc[a, "game_id"]
        players_using = agent_stats.loc[a, "name"]
        agent_labels.append(f"{a}\n{total_picks} picks\n{players_using} players")

    all_nodes = player_labels + agent_labels

    # Create direct player → agent flow
    node_dict = {}
    for i, (original, enhanced) in enumerate(zip(players + agents, all_nodes)):
        node_dict[original] = i

    # Color nodes
    node_colors = ["rgba(70, 130, 180, 0.8)"] * len(
        players
    ) + [  # Steel blue for players
        "rgba(34, 139, 34, 0.8)"
    ] * len(
        agents
    )  # Forest green for agents

    sources, targets, values, link_colors, hover_labels = [], [], [], [], []

    # Create player → agent direct connections
    player_agent_picks = (
        players_map_agent_pool.groupby(["name", "agent"])["game_id"].sum().reset_index()
    )

    for _, row in player_agent_picks.iterrows():
        sources.append(node_dict[row["name"]])
        targets.append(node_dict[row["agent"]])
        values.append(row["game_id"])

        # Color based on pick frequency
        max_picks = player_agent_picks["game_id"].max()
        intensity = 0.3 + (row["game_id"] / max_picks) * 0.5
        link_colors.append(f"rgba(255, 99, 71, {intensity})")  # Tomato color

        # Get map details for this player-agent combo
        maps_played = players_map_agent_pool[
            (players_map_agent_pool["name"] == row["name"])
            & (players_map_agent_pool["agent"] == row["agent"])
        ]["map"].tolist()
        hover_labels.append(
            f"{row['name']} → {row['agent']}<br>Picked {row['game_id']} times<br>Maps: {', '.join(maps_played)}"
        )

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=25,
                    thickness=30,
                    line=dict(color="black", width=1.5),
                    label=all_nodes,
                    color=node_colors,
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color=link_colors,
                    customdata=hover_labels,
                    hovertemplate="%{customdata}<extra></extra>",
                ),
            )
        ]
    )

    fig.update_layout(
        title={
            "text": "Player Agent Preferences<br><sub>Direct flow showing who prefers which agents</sub>",
            "x": 0.5,
            "font": {"size": 18, "color": "darkgreen"},
        },
    )

    return fig
