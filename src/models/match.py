from typing import Iterator
from datetime import datetime
import pandas as pd
import numpy as np
from .game import Game, Games


class Match:
    def __init__(
        self,
        match_id: int,
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
        games: Games,
    ) -> None:
        self.match_id = match_id
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
            game_data, columns=np.array(["game_id", "map_name", "winner"])
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


class Matches:
    def __init__(self, matches: list[Match]):
        self.matches = matches
        self.by_id = {match.match_id: match for match in matches}

    def __getitem__(self, match_id: int) -> Match:
        return self.by_id[match_id]

    def __len__(self) -> int:
        return len(self.matches)

    def __iter__(self) -> Iterator[Match]:
        return iter(self.by_id.values())
