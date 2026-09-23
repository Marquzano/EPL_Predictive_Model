import datetime
from fastapi import Request, APIRouter
from modeling import make_tensors
from api.features import get_team_form
from api.schemas import PredictRequest, PredictResponse

# make the route object to define routes
router = APIRouter()

# define /predict as a post whenever a request is made
@router.post('/predict', response_model=PredictResponse)
def predict(request:Request, payload:PredictRequest):
    # pull the yielded objects at app startup
    model = request.state.model
    con = request.state.con
    scaler = request.state.scaler
    # as of the date of execution for now
    as_of_date = datetime.date.today().isoformat()

    # pull team form from features.py
    # and give the yielded con and other
    # values from the request
    home_team_form = get_team_form(con=con, team_id=payload.home_team_id, as_of_date=as_of_date)
    away_team_form = get_team_form(con=con, team_id=payload.away_team_id, as_of_date=as_of_date)

    # make the input shapes as the model expects it
    # stats shape - (1,10)
    # categorical shape - (1,2)
    stats_input = [home_team_form + away_team_form]
    cat_input = [[payload.home_team_id, payload.away_team_id]]

    # scale the stats according to the
    # scaler created in training
    scaled_stats = scaler.transform(stats_input)

    # make the inputs into tensors
    cat_tensor, stats_tensor = make_tensors(cat_input, scaled_stats)

    # run the prediction from the model
    prediction = model.predict([cat_tensor, stats_tensor])

    # get the probabilities from the prediction matrix
    probabilites = prediction[0]

    # return each probability according
    # to the class PredictResponse for FastAPI
    return PredictResponse(home_win_probability=probabilites[0], away_win_probability=probabilites[1], draw_probability=probabilites[2])