from models import MatchHistory
import pandas as pd


def get_players_agent_pool(matches: MatchHistory):
    team_df = matches.overview.xs(matches.short_name, level="team")
    all_cols = [col for col in team_df if col.endswith("_all")]
    aggregations = {"game_id": "count"}
    for col in all_cols:
        aggregations[col] = "mean"
    agent_stats = team_df.reset_index().groupby(["name", "agent"]).agg(aggregations)
    return agent_stats


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
