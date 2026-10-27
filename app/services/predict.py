import pandas as pd
from pipeline.modeling import make_tensors

# pull the team form from the five trailing matches
# prior to the as_of_date
# for now it pulls from the DB as we don't have
# live data
def get_team_form(con, team_id, as_of_date):
    query = 'SELECT gf, xg, poss, sh, sot FROM match_data' \
    '        WHERE team_id = ? AND date < ?' \
    '        ORDER BY date DESC, time DESC, round DESC' \
    '        LIMIT 5;'

    team_form = pd.read_sql(query, con=con, params=(team_id, as_of_date))

    if len(team_form) < 5:
        return [-1, -1, -1, -1, -1]
    else:
        return team_form.mean().tolist()

def predict_match(model, con, scaler, as_of_date, home_id, away_id):
    # pull team form
    # and give the yielded con and other
    # values from the request
    home_team_form = get_team_form(con=con, team_id=home_id, as_of_date=as_of_date)
    away_team_form = get_team_form(con=con, team_id=away_id, as_of_date=as_of_date)

    # make the input shapes as the model expects it
    # stats shape - (1,10)
    # categorical shape - (1,2)
    stats_input = [home_team_form + away_team_form]
    cat_input = [[home_id, away_id]]

    # scale the stats according to the
    # scaler created in training
    scaled_stats = scaler.transform(stats_input)

    # make the inputs into tensors
    cat_tensor, stats_tensor = make_tensors(cat_input, scaled_stats)

    # run the prediction from the model
    prediction = model.predict([cat_tensor, stats_tensor])

    # get the probabilities from the prediction matrix
    probabilities = prediction[0]

    return probabilities