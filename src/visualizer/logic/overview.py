from models import MatchHistory
import pandas as pd


def get_team_win_lose(matches: MatchHistory) -> pd.DataFrame:
    games_data = matches.games_data
    games_data["result"] = games_data["winner"].map(
        lambda x: "win" if x == matches.full_name else "lose"
    )
    map_win_lose = games_data.groupby(["result", "map_name"]).count()
    return map_win_lose


def get_team_pistol_impact(matches: MatchHistory) -> pd.DataFrame:
    total_pistol = len(matches.games) * 2
    total_pistol_win = 0
    total_second_round = len(matches.games)
    total_second_round_win = 0
    total_2_round_win = 0
    for game in matches.games:
        if len(game.round_result) > 13:
            total_second_round += 1

        for base_round in [0, 12]:
            if (
                game.round_result.iloc[base_round + 0].winning_team
                == matches.short_name
            ):
                total_pistol_win += 1

            if ((base_round + 1) < len(game.round_result)) and (
                game.round_result.iloc[base_round + 1].winning_team
                == matches.short_name
            ):
                total_second_round_win += 1

            if (
                game.round_result.iloc[base_round + 0].winning_team
                == matches.short_name
            ) and (
                ((base_round + 1) < len(game.round_result))
                and (
                    game.round_result.iloc[base_round + 1].winning_team
                    == matches.short_name
                )
            ):
                total_2_round_win += 1

    return pd.DataFrame(
        {
            "pistol": [total_pistol, total_pistol_win, total_pistol_win / total_pistol],
            "second_round": [
                total_second_round,
                total_second_round_win,
                total_second_round_win / total_second_round,
            ],
            "2_round": [
                total_second_round,
                total_2_round_win,
                total_2_round_win / total_second_round,
            ],
            "type": ["total", "win", "prob"],
        }
    ).set_index("type")


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
