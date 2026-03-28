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

def rolled_averages(con=None, df=None):
    # we could go season by season
    # this way you can handle relegated teams easier
    # season = 2021
    season_21_df = df[df['season'] == 2021]

    # practice query to calculate rolling average windows using SQL
    #     SELECT
    #    ...> date,
    #    ...> time,
    #    ...> round,
    #    ...> result,
    #    ...> gf,
    #    ...> AVG(gf) OVER (PARTITION BY team ORDER BY date, time, round, season ROWS 5 PRECEDING) AS avg_5_gf,
    #    ...> ga,
    #    ...> AVG(ga) OVER (PARTITION BY team ORDER BY date, time, round, season ROWS 5 PRECEDING) AS avg_5_ga,
    #    ...> team,
    #    ...> season
    #    ...> FROM match_data LIMIT 10;

    # second attempt, this does the rolling average window calculations I am wanting
    #     SELECT
    #    ...> date,
    #    ...> time,
    #    ...> round,
    #    ...> result,
    #    ...> gf,
    #    ...> AVG(gf) OVER(PARTITION BY team ORDER BY date, time, round, season ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_gf,
    #    ...> ga,
    #    ...> AVG(ga) OVER(PARTITION BY team ORDER BY date, time, round, season ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_ga,
    #    ...> team,
    #    ...> season
    #    ...> FROM match_data LIMIT 30;

    # now I need to modify the query so that the first 5 matches 
    # that don't have exactly 5 previous matches default to -1
    # for all their stat columns
    

    return None

if __name__ == '__main__':
    clean_csv = 'data/processed/clean_final_matches.csv'
    db_path = 'data/processed/EPL_data.db'

    con, cur, clean_df = open_con(db_path, clean_csv, 'match_data')

    rolled_averages(df=clean_df)
    
    # merging rows to have single-row unique matches
    merged_df = make_matches(clean_df)

    merged_df.to_csv('data/processed/old_merged_matches.csv')

    merged_df.to_sql('old_merged_matches', con=con, if_exists='replace', index=False)

    # cleaning up the data to necessary keys, features, and labels
    clean_merged_df = clean_matches(con)

    clean_merged_df.to_csv('data/processed/merged_matches.csv')

    clean_merged_df.to_sql('merged_matches', con=con, if_exists='replace', index=False)
