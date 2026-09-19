#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import pandas as pd

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