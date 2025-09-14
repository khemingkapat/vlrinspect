from models import MatchHistory
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
