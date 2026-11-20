import pandas as pd
from pipeline.modeling import make_tensors

# pull the team form from the five trailing matches
# prior to the as_of_date
# This now pulls from live data
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

# function to handle label encoding for predictions
def to_probabilities(row):
    return {
        'home_win_probability': round(float(row[0]), 5),
        'away_win_probability': round(float(row[1]), 5),
        'draw_probability': round(float(row[2]), 5)
    }

def predict_matches(model, con, scaler, matches):
    if not matches:
        return []

    stats_rows = []
    cat_rows = []
    insufficient = []

    for m in matches:
        home_form = get_team_form(con, m['home_id'], m['as_of_date'])
        away_form = get_team_form(con, m['away_id'], m['as_of_date'])
        stats_rows.append(home_form + away_form)
        cat_rows.append([m['home_id'], m['away_id']])
        insufficient.append(-1 in home_form + away_form) # shouldn't this be a comment?

    scaled_stats = scaler.transform(stats_rows)
    cat_tensor, stats_tensor = make_tensors(cat_rows, scaled_stats)
    predictions = model.predict([cat_tensor, stats_tensor], verbose=0)

    return [{**to_probabilities(p), 'insufficient_data': flag}
            for p, flag in zip(predictions, insufficient)]

def predict_match(model, con, scaler, as_of_date, home_id, away_id):
    match = {'home_id': home_id, 'away_id': away_id, 'as_of_date': as_of_date}
    return predict_matches(model, con, scaler, [match])[0]