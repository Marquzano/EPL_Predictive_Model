import datetime
from fastapi import Request, APIRouter
from modeling import make_tensors
from api.features import get_team_form
from api.schemas import PredictRequest, PredictResponse

router = APIRouter()

@router.post('/predict')
def predict(request:Request, payload:PredictRequest):
    model = request.state.model
    con = request.state.con
    scaler = request.state.scaler
    as_of_date = datetime.date.today().isoformat()

    home_team_form = get_team_form(con=con, team_id=payload.home_team_id, as_of_date=as_of_date)
    away_team_form = get_team_form(con=con, team_id=payload.away_team_id, as_of_date=as_of_date)

    stats_input = [home_team_form + away_team_form]
    cat_input = [[payload.home_team_id, payload.away_team_id]]

    scaled_stats = scaler.transform(stats_input)

    cat_tensor, stats_tensor = make_tensors(cat_input, scaled_stats)

    prediction = model.predict([cat_tensor, stats_tensor])

    probabilites = prediction[0]

    return PredictResponse(home_win_probability=probabilites[0], away_win_probability=probabilites[1], draw_probability=probabilites[2])