from models import MatchHistory
import pandas as pd
from sklearn.preprocessing import StandardScaler


def get_players_agent_pool(matches, apply_composite_scores: bool = False):

    team_df = matches.overview.xs(matches.short_name, level="team")
    all_cols = [col for col in team_df if col.endswith("_all")]
    aggregations = {"game_id": "count"}
    for col in all_cols:
        aggregations[col] = "mean"
    agent_stats = team_df.reset_index().groupby(["name", "agent"]).agg(aggregations)

    if not apply_composite_scores:
        return agent_stats

    individual_performance_stats = {
        "k_all": 0.25,
        "acs_all": 0.25,
        "adr_all": 0.20,
        "r2_0_all": 0.15,
        "hs%_all": 0.10,
        "d_all": -0.05,
    }

    team_contribution_stats = {
        "a_all": 0.30,
        "kast_all": 0.25,
        "fk_all": 0.15,
        "fd_all": -0.15,
        "f+/-_all": 0.15,
        "+/-_all": 0.10,
    }

    scoring_data = agent_stats[all_cols].copy()
    scoring_data = scoring_data.fillna(0)

    scaler = StandardScaler()
    scoring_data_scaled = pd.DataFrame(
        scaler.fit_transform(scoring_data),
        columns=scoring_data.columns,
        index=scoring_data.index,
    )

    individual_performance = pd.Series(0, index=scoring_data_scaled.index)
    available_individual_stats = []

    for stat, weight in individual_performance_stats.items():
        if stat in scoring_data_scaled.columns:
            individual_performance += scoring_data_scaled[stat] * weight
            available_individual_stats.append(
                f"{stat.replace('_all', '')} ({weight:.0%})"
            )

    team_contribution = pd.Series(0, index=scoring_data_scaled.index)
    available_team_stats = []

    for stat, weight in team_contribution_stats.items():
        if stat in scoring_data_scaled.columns:
            team_contribution += scoring_data_scaled[stat] * weight
            available_team_stats.append(f"{stat.replace('_all', '')} ({weight:.0%})")

    composite_df = pd.DataFrame(
        {
            "Individual Performance": individual_performance,
            "Team Contribution": team_contribution,
        },
        index=agent_stats.index,
    )

    composite_df["game_id"] = agent_stats["game_id"]

    return composite_df


def get_player_stats(matches: MatchHistory, cat_by: str = "side") -> pd.DataFrame:
    team_df = matches.overview.xs(matches.short_name, level="team")
    win_game_ids = [
        game.game_id for game in matches.games if game.winner == matches.full_name
    ]
    if cat_by == "win":
        win_idx = team_df.index.get_level_values("game_id").isin(win_game_ids)
        col_all = team_df.columns.str.endswith("_all")
        cat1_df = team_df.loc[win_idx, col_all]
        cat2_df = team_df.loc[~win_idx, col_all]

        cat1_df = cat1_df.rename(
            columns={col: col.removesuffix("_all") for col in cat1_df.columns},
        )
        cat2_df = cat2_df.rename(
            columns={col: col.removesuffix("_all") for col in cat2_df.columns},
        )
        cat1_id = "win"
        cat2_id = "lose"
    else:
        cat1_df = team_df.loc[:, team_df.columns.str.endswith("_atk")]
        cat2_df = team_df.loc[:, team_df.columns.str.endswith("_def")]

        cat1_df = cat1_df.rename(
            columns={col: col.removesuffix("_atk") for col in cat1_df.columns},
        )
        cat2_df = cat2_df.rename(
            columns={col: col.removesuffix("_def") for col in cat2_df.columns},
        )
        cat1_id = "atk"
        cat2_id = "def"

    player_cat1 = (
        cat1_df.select_dtypes(exclude="object")
        .groupby(level="name")
        .mean()
        .reset_index()
    )
    player_cat2 = (
        cat2_df.select_dtypes(exclude="object")
        .groupby(level="name")
        .mean()
        .reset_index()
    )

    player_cat1["cat"] = cat1_id
    player_cat2["cat"] = cat2_id
    combined = pd.concat([player_cat1, player_cat2])
    return combined.rename(
        columns={
            "r2.0": "Rating 2.0",
            "acs": "ACS",
            "k": "Kill",
            "d": "Death",
            "a": "Assist",
            "+/–": "KD Diff",
            "kast": "KAST",
            "adr": "ADR",
            "hs%": "Headshot %",
            "fk": "First Kill",
            "fd": "First Death",
            "f+/–": "FKD Diff",
        },
    )


def get_player_stat_history(
    matches: MatchHistory, stat_column: str = "Rating 2.0"
) -> pd.DataFrame:
    overview = matches.overview.xs(matches.short_name, level="team")

    abbr = {
        "Rating 2.0": "r2.0",
        "ACS": "acs",
        "Kill": "k",
        "Death": "d",
        "Assist": "a",
        "KD Diff": "+/–",
        "KAST": "kast",
        "ADR": "adr",
        "Headshot %": "hs%",
        "First Kill": "fk",
        "First Death": "fd",
        "FKD Diff": "f+/–",
    }

    column_name = abbr[stat_column] + "_all"

    pivoted_df = overview[[column_name]].pivot_table(
        index="game_id",
        columns="name",
        values=column_name,
        aggfunc="first",
    )
    return pivoted_df
