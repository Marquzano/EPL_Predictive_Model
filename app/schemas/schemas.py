#######################################
# The schemas here are for FastAPI to
# maintain the "shape" for requests and
# responses when running the lifespan of
# the app
#######################################
from pydantic import BaseModel

class PredictRequest(BaseModel):
    home_team_id: int
    away_team_id: int
    # will include the below once we have live data
    # determine type later
    # as_of_date: str

class PredictResponse(BaseModel):
    home_win_probability: float
    away_win_probability: float
    draw_probability: float

class TeamResponse(BaseModel):
    team_id: int
    team: str