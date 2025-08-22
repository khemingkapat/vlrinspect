from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
import pandas as pd


class Match(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    patch: float
    teams: list[str]
    event_name: str
    match_date: datetime
    patch: float
    match_result: dict[str, int]
    team_abbreviation: dict[str, str]

    pick_ban: pd.DataFrame
    round_result: pd.DataFrame
    overview: pd.DataFrame

    def __str__(self) -> str:
        winner = max(self.match_result, key=self.match_result.get)
        return (
            f"{self.event_name}\n"
            f"{' vs '.join(self.teams)}\n"
            f"Date: {self.match_date.date()}\n"
            f"Winner: {winner} ({self.match_result})"
        )

    def __repr__(self) -> str:
        return f"Match({self.teams[0]} vs {self.teams[1]} - {self.event_name})"
