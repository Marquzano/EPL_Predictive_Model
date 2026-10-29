import pandas as pd

def get_teams(con):
    query = 'SELECT team_id, team FROM team_registry ORDER BY team;'
    teams = pd.read_sql(query, con=con)

    return teams.to_dict(orient='records')