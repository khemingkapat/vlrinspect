from models import MatchHistory
import pandas as pd


def get_team_win_lose(matches: MatchHistory) -> pd.DataFrame:
    win_lose_count = matches.matches_data["result"].value_counts().reset_index()
    win_lose_count.columns = ["outcome", "count"]
    return win_lose_count


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


def get_team_buy_type_win_lose(matches: MatchHistory) -> pd.DataFrame:
    round_result = matches.round_result

    win_idx = round_result.winning_team == matches.short_name

    win_df = round_result[win_idx]
    lose_df = round_result[~win_idx]

    result = pd.DataFrame()
    result["win"] = win_df.winner_buytype.value_counts()
    result["lose"] = lose_df.loser_buytype.value_counts()
    result["total"] = result.sum(axis=1)
    return result


def get_team_win_condition(matches: MatchHistory) -> pd.DataFrame:
    round_result = matches.round_result

    win_idx = round_result.winning_team == matches.short_name

    win_df = round_result[win_idx]
    lose_df = round_result[~win_idx]

    result = pd.DataFrame()
    result["win"] = win_df.reason.value_counts()
    result["lose"] = lose_df.reason.value_counts()
    result["total"] = result.sum(axis=1)
    return result
