from models.match_history import MatchHistory
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

    melted_df = team_pick_ban.melt(
        id_vars=["map"],
        value_vars=["pick", "ban"],
        var_name="action",
        value_name="count",
    )

    fig = px.bar(
        melted_df,
        x="map",
        y="count",
        color="action",
        barmode="group",
        color_discrete_map={"ban": "#FF6B6B", "pick": "#4ECDC4"},
        title=f"{matches.full_name}'s Pick and Ban Counts by Map",
        labels={"count": "Count", "map": "Map", "action": "Action"},
    )

    return fig


def plot_team_side_bias(matches: MatchHistory) -> Figure:
    team_side_win = get_team_side_bias(matches).reset_index().sort_values("win_rate")

    fig = px.bar(
        team_side_win,
        x="map",
        y="win_rate",
        color="team_side",
        color_discrete_map={"atk": "#FF6B6B", "def": "#4ECDC4"},
        barmode="group",
        title=f"{matches.full_name}'s Side Bias",
        labels={"win_rate": "Win Rate (%)", "map": "Map", "team_side": "Side"},
    )
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
        font_size=12,
        width=1200,
        height=700,
        paper_bgcolor="rgba(245, 255, 245, 1)",
    )

    return fig
