#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import pandas as pd
import sqlite3

# open connection to the DB first
def open_con(db_path, csv_path, table_name):
    # create the connection
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # open csv file as a dataframe
    df = pd.read_csv(csv_path, na_filter=True)
    # load the dataframe as a table
    df.to_sql(table_name, con=con, if_exists='replace', index=False)
    
    return con, cur, df

def make_matches(df):
    id_cols = ['season', 'date', 'time', 'round']

    # splitting up df into home and away matches to be merged into unique match rows
    home_df = df[df['venue'] == 'Home'].copy()
    away_df = df[df['venue'] == 'Away'].copy()

    # renaming columns accordingly to later clean and consolidate
    home_df = home_df.rename(columns={c: f"{c}_home" for c in home_df.columns if c not in id_cols})
    away_df = away_df.rename(columns={c: f"{c}_away" for c in away_df.columns if c not in id_cols})

    # merging into one df
    merged_df = pd.merge(home_df, away_df, on=id_cols)

    # removing inconsistencies where matches merge on id_cols but are not the same match
    merged_df = merged_df[merged_df['opponent_home'] == merged_df['team_away']]

    # renaming columns team_home and team_away for simplicity
    merged_df = merged_df.rename(columns={'team_home': 'home', 'team_away':'away'})

    # below I'm making a single column to hold the result for each unique match
    data = []

    for value in merged_df['result_home']:
        if value == 'W':
            data.append('Home')
        elif value == 'L':
            data.append('Away')
        else:
            data.append('Draw')
    
    result = pd.Series(data)
    merged_df['result'] = result.values

    return merged_df

def clean_matches(con):
    # selecting the needed features and omitting others
    # also ordering the matches in chronological order
    query = 'SELECT season, date, time, round, gf_home, xg_home, poss_home, sh_home, sot_home, home, gf_away, xg_away, poss_away, sh_away, sot_away, away, result FROM old_merged_matches ORDER BY date, time, round;'
    df = pd.read_sql(query, con=con)

    return df

def rolled_averages(con):
    # use the connection to query match_data
    # the query will run the rolled average calculations
    # as well as the formatting for the result set
    query = ('SELECT sub.date, sub.time, sub.round, sub.venue, sub.result, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_gf END AS avg_5_gf, sub.opponent, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_xg END AS avg_5_xg, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_poss END AS avg_5_poss, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_sh END AS avg_5_sh, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_sot END AS avg_5_sot, sub.team, sub.season FROM (SELECT *, ROW_NUMBER() OVER w AS team_index, AVG(gf) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_gf, AVG(xg) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_xg, AVG(poss) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_poss, AVG(sh) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_sh, AVG(sot) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_sot FROM match_data WINDOW w AS (PARTITION BY team ORDER BY date, time, round, season)) sub;')

    df = pd.read_sql(query, con=con)
    return df

if __name__ == '__main__':
    clean_csv = 'data/processed/clean_final_matches.csv'
    db_path = 'data/processed/EPL_data.db'

    con, cur, clean_df = open_con(db_path, clean_csv, 'match_data')

    rolled_averages_df = rolled_averages(con)

    # need to review the next steps to be sure I am not missing
    # on any useful data sets
    
    # merging rows to have single-row unique matches
    merged_df = make_matches(clean_df)

    merged_df.to_csv('data/processed/old_merged_matches.csv')

    merged_df.to_sql('old_merged_matches', con=con, if_exists='replace', index=False)

    # cleaning up the data to necessary keys, features, and labels
    clean_merged_df = clean_matches(con)

    clean_merged_df.to_csv('data/processed/merged_matches.csv')

    clean_merged_df.to_sql('merged_matches', con=con, if_exists='replace', index=False)
