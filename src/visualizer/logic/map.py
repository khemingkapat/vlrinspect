from src.models import MatchHistory
import pandas as pd


def get_team_pick_ban(matches: MatchHistory) -> pd.DataFrame:
    all_pick_ban = []
    for match in matches:
        if not match.pick_ban.empty:
            all_pick_ban.append(match.pick_ban)

    team_pick_ban = (
        pd.concat(all_pick_ban)
        .loc[matches.full_name]
        .reset_index()
        .drop("team", axis=1)
    )

    pick_ban_count = (
        team_pick_ban.groupby(["map", "action"]).size().unstack(fill_value=0)
    )
    return pick_ban_count.sort_values(["pick", "ban"], ascending=False)


def get_players_map_agent_pool(matches: MatchHistory):
    team_df = matches.overview.xs(matches.short_name, level="team")
    all_cols = [col for col in team_df if col.endswith("_all")]

    aggregations = {"game_id": "count"}
    for col in all_cols:
        aggregations[col] = "mean"
    agent_map_stats = (
        team_df.reset_index().groupby(["name", "map", "agent"]).agg(aggregations)
    )
    return agent_map_stats


def get_team_side_bias(matches: MatchHistory) -> pd.DataFrame:
    round_result = matches.round_result

    def get_team_side_and_result(row, team_name):
        if row["atk_team"] == team_name:
            return "atk", row["winning_side"] == "atk"
        else:
            return "def", row["winning_side"] == "def"

    round_result[["team_side", "team_won"]] = round_result.apply(
        lambda row: get_team_side_and_result(row, matches.short_name),
        axis=1,
        result_type="expand",
    )

    team_performance_summary = round_result.groupby(["map", "team_side"]).agg(
        rounds_won=("team_won", "sum"), total_rounds=("team_won", "count")
    )

    team_performance_summary.loc[:, "win_rate"] = (
        team_performance_summary["rounds_won"]
        / team_performance_summary["total_rounds"]
    ).round(2)

    return team_performance_summary


def get_map_pistol_impact(matches: MatchHistory) -> pd.DataFrame:
    games_data = matches.games_data.reset_index()
    all_df = []

    for map in games_data.map_name.unique():
        n_games = (games_data.map_name == map).sum()

        total_pistol = n_games * 2
        total_pistol_win = 0
        total_second_round = n_games
        total_second_round_win = 0
        total_2_round_win = 0

        games = [game for game in matches.games if game.map_name == map]

        for game in games:
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

        all_df.append(
            pd.DataFrame(
                {
                    "pistol": [
                        total_pistol,
                        total_pistol_win,
                        total_pistol_win / total_pistol,
                    ],
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
                    "map_name": [map] * 3,
                }
            )
        )

    return pd.concat(all_df).set_index(["map_name", "type"])
