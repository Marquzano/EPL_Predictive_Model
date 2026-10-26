import pandas as pd

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