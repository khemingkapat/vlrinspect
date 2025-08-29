from typing import Iterator
from datetime import datetime
import pandas as pd
from .game import Game


class Match:
    def __init__(
        self,
        patch: float,
        teams: list[str],
        event_name: str,
        stage_name: str,
        match_date: datetime,
        match_result: dict[str, int],
        team_abbreviation: dict[str, str],
        winner: str,
        match_url: str,
        pick_ban: pd.DataFrame,
        games: list[Game],
    ) -> None:
        self.patch = patch
        self.teams = teams
        self.event_name = event_name
        self.stage_name = stage_name
        self.match_date = match_date
        self.match_result = match_result
        self.team_abbreviation = team_abbreviation
        self.winner = winner
        self.match_url = match_url
        self.pick_ban = pick_ban
        self.games = games

        game_data = []
        for game in games:
            game_data.append([game.game_id, game.map_name, game.winner])
        self.games_data = pd.DataFrame(
            game_data, columns=["game_id", "map_name", "winner"]
        ).set_index("game_id")

    def __str__(self) -> str:
        return (
            f"{'-'*50}\n"
            f"{self.event_name}\n"
            f"{' vs '.join(self.teams)}\n"
            f"Date: {self.match_date.date()}\n"
            f"Winner: {self.winner} ({self.match_result})\n"
            f"{'-'*50}"
        )

    def __repr__(self) -> str:
        return f"Match({self.teams[0]} vs {self.teams[1]} - {self.event_name})"

    def __iter__(self) -> Iterator[Game]:
        return iter(self.games)


class MatchHistory:
    def __init__(self, full_name: str, short_name: str, matches: list[Match]):
        self.matches = matches
        self.full_name = full_name
        self.short_name = short_name

        # self.overview = pd.DataFrame()
        # self.round_result = pd.DataFrame()
        # self.matches = pd.DataFrame()

        matches_data = []
        for match in self.matches:
            match_id = int(
                match.match_url.removeprefix("https://www.vlr.gg/").split("/")[0]
            )
            opp_team = match.teams[0]
            if opp_team == self.full_name:
                opp_team = match.teams[1]

            # self.overview = pd.concat([self.overview, match.overview])
            # self.round_result = pd.concat([self.round_result, match.round_result])
            matches_data.append(
                [
                    match_id,
                    match.event_name,
                    match.stage_name,
                    match.match_date,
                    opp_team,
                    match.match_result[self.full_name],
                    match.match_result[opp_team],
                    "win" if match.winner == self.full_name else "lose",
                ]
            )

        self.matches_data = pd.DataFrame(
            matches_data,
            columns=[
                "match_id",
                "event_name",
                "stage_name",
                "match_date",
                "opp_team",
                "team_score",
                "opp_score",
                "result",
            ],
        ).set_index("match_id")

    def __repr__(self) -> str:
        return f"{self.full_name}'s History"

    def __iter__(self) -> Iterator[Match]:
        return iter(self.matches_list)

    def __len__(self) -> int:
        return len(self.matches_list)
