import pandas as pd
from .match import Match, Matches
from .game import Games
from typing import Iterator
import numpy as np
from functools import cached_property
from datetime import datetime


class MatchHistory:
    def __init__(self, full_name: str, short_name: str, matches: Matches):
        self.matches = matches
        self.full_name = full_name
        self.short_name = short_name

        # self.overview = pd.DataFrame()
        # self.round_result = pd.DataFrame()
        # self.matches = pd.DataFrame()

    @cached_property
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
        all_game_data: list[pd.DataFrame] = []
        for match in self.matches:
            all_game_data.append(match.games_data)

        return pd.concat(all_game_data)

    @cached_property
    def overview(self) -> pd.DataFrame:
        all_overview_data = []
        for match in self.matches:
            for game in match.games:
                all_overview_data.append(game.overview)
        return pd.concat(all_overview_data)

    @cached_property
    def round_result(self) -> pd.DataFrame:
        all_round_result = []
        for match in self.matches:
            for game in match.games:
                all_round_result.append(game.round_result)
        return pd.concat(all_round_result)

    @cached_property
    def games(self) -> Games:
        all_games = []
        for match in self.matches:
            all_games.extend(match.games.games)
        return Games(all_games)

    def filter_matches(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        patch: float | None = None,
        event_name: str | None = None,
        since_event: str | None = None,
        map_names: list[str] = [],
    ) -> "MatchHistory":
        since_date = None
        if since_event:
            event_dates = []
            for match in self.matches:
                if (
                    match.event_name.lower() == since_event.lower()
                    or since_event.lower() in match.event_name.lower()
                ):
                    event_dates.append(match.match_date)

            if event_dates:
                since_date = min(event_dates)

        filtered_matches = []
        for match in self.matches:
            if start_date and match.match_date < start_date:
                continue
            if end_date and match.match_date > end_date:
                continue
            if since_date and match.match_date < since_date:
                continue
            if patch and match.patch != patch:
                continue
            if event_name and (
                match.event_name.lower() != event_name.lower()
                and event_name.lower() not in match.event_name.lower()
            ):
                continue
            if map_names:
                filtered_games = []
                for game in match.games:
                    if game.map_name in map_names:
                        filtered_games.append(game)
                if not filtered_games:
                    continue
                new_games = Games(filtered_games)
                new_match = Match(
                    match_id=match.match_id,
                    patch=match.patch,
                    teams=match.teams,
                    event_name=match.event_name,
                    stage_name=match.stage_name,
                    match_date=match.match_date,
                    match_result=match.match_result,
                    team_abbreviation=match.team_abbreviation,
                    winner=match.winner,
                    match_url=match.match_url,
                    pick_ban=match.pick_ban,
                    games=new_games,
                )
                filtered_matches.append(new_match)
            else:
                filtered_matches.append(match)
        new_matches_collection = Matches(filtered_matches)
        return MatchHistory(self.full_name, self.short_name, new_matches_collection)

    def __repr__(self) -> str:
        return f"{self.full_name}'s History"

    def __iter__(self) -> Iterator[Match]:
        return iter(self.matches)

    def __len__(self) -> int:
        return len(self.matches)

    def __getitem__(self, match_id: int) -> Match:
        return self.matches[match_id]
