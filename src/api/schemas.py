from pydantic import BaseModel

class PredictRequest(BaseModel):
    home_team_id: int
    away_team_id: int

class PredictResponse(BaseModel):
    home_win_probability: float
    away_win_probability: float
    draw_probability: float

class Team(BaseModel):
    team_id: int
    team: str