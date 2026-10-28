import datetime
from fastapi import Request, APIRouter, Depends
from typing import Annotated
import sqlite3
from app.api.dependencies import get_con
from app.services.predict import predict_match
from app.schemas.schemas import PredictRequest, PredictResponse

# make the route object to define routes
router = APIRouter()

# define /predict as a post whenever a request is made
@router.post('/predict', response_model=PredictResponse)
def predict(request:Request, payload:PredictRequest, con: Annotated[sqlite3.Connection, Depends(get_con)]):
    # we need to pass the necessary objects to the 
    # services layer which handles the logic for the backend
    # pull the yielded objects at app startup
    model = request.state.model
    scaler = request.state.scaler
    # as of the date of execution for now
    as_of_date = datetime.date.today().isoformat()
    # get home and away IDs from the payload object (PredictRequest)
    home_id = payload.home_team_id
    away_id = payload.away_team_id

    result = predict_match(model, con, scaler, as_of_date, home_id, away_id)

    # return each probability according
    # to the class PredictResponse for FastAPI
    return PredictResponse(**result)