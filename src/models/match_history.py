import pandas as pd
from .match import Match, Matches
from .game import Games
from typing import Iterator
import numpy as np
from functools import cached_property


class MatchHistory:
    def __init__(self, full_name: str, short_name: str, matches: Matches):
        self.matches = matches
        self.full_name = full_name
        self.short_name = short_name

        # self.overview = pd.DataFrame()
        # self.round_result = pd.DataFrame()
        # self.matches = pd.DataFrame()

    @property
    def matches_data(self) -> pd.DataFrame:
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

        return pd.DataFrame(
            matches_data,
            columns=np.array(
                [
                    "match_id",
                    "event_name",
                    "stage_name",
                    "match_date",
                    "opp_team",
                    "team_score",
                    "opp_score",
                    "result",
                ]
            ),
        ).set_index("match_id")

    @cached_property
    def games_data(self) -> pd.DataFrame:
        games_data = pd.DataFrame()
        for match in self.matches:
            games_data = pd.concat([games_data, match.games_data])

        return games_data

    @cached_property
    def overview(self) -> pd.DataFrame:
        overview = pd.DataFrame()
        for match in self.matches:
            for game in match.games:
                overview = pd.concat([overview, game.overview])
        return overview

    @cached_property
    def round_result(self) -> pd.DataFrame:
        round_result = pd.DataFrame()
        for match in self.matches:
            for game in match.games:
                round_result = pd.concat([round_result, game.round_result])
        return round_result

    @cached_property
    def games(self) -> Games:
        all_games = []
        for match in self.matches:
            all_games.extend(match.games.games)
        return Games(all_games)

    def __repr__(self) -> str:
        return f"{self.full_name}'s History"

    def __iter__(self) -> Iterator[Match]:
        return iter(self.matches)

    def __len__(self) -> int:
        return len(self.matches)

    def __getitem__(self, match_id: int) -> Match:
        return self.matches[match_id]
