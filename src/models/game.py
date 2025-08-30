from pydantic import BaseModel, ConfigDict
import pandas as pd
from typing import Iterator


class Game(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    map_name: str
    game_id: int
    winner: str

    round_result: pd.DataFrame
    overview: pd.DataFrame

    def __repr__(self) -> str:
        return f"Game(map_name={self.map_name}, game_id={self.game_id})"

    def __str__(self) -> str:
        return f"Game(map_name={self.map_name}, game_id={self.game_id})"


class Games:
    def __init__(self, games: list[Game]):
        self.games = games
        self.by_id = {game.game_id: game for game in games}

    def __getitem__(self, game_id: str) -> Game:
        return self.by_id[game_id]

    def __len__(self) -> int:
        return len(self.games)

    def __iter__(self) -> Iterator[Game]:
        return iter(self.by_id.values())
