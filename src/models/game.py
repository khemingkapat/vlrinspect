from pydantic import BaseModel, ConfigDict
import pandas as pd


class Game(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    map_name: str
    game_id: str
    map_winner: str

    round_result: pd.DataFrame
    overview: pd.DataFrame

    def __repr__(self) -> str:
        return f"Game(map_name={self.map_name}, game_id={self.game_id})"

    def __str__(self) -> str:
        return f"Game(map_name={self.map_name}, game_id={self.game_id})"
