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

    home_df = df[df['venue'] == 'Home'].copy()
    away_df = df[df['venue'] == 'Away'].copy()

    home_df = home_df.rename(columns={c: f"{c}_home" for c in home_df.columns if c not in id_cols})
    away_df = away_df.rename(columns={c: f"{c}_away" for c in away_df.columns if c not in id_cols})

    merged_df = pd.merge(home_df, away_df, on=id_cols)

    print(merged_df.head()) 

    return merged_df

if __name__ == '__main__':
    clean_csv = 'data/processed/clean_final_matches.csv'
    db_path = 'data/processed/EPL_data.db'

    con, cur, clean_df = open_con(db_path, clean_csv, 'match_data')

    # I want to combine rows that have data corresponding to a single match
    # make a function that takes the df and finds the rows with matching
    # matchweek
    # date
    # season
    merged_df = make_matches(clean_df)

    merged_df.to_csv('data/processed/merged_matches.csv')

    merged_df.to_sql('merged_matches', con=con, if_exists='replace', index=False)

    # need to remove some columns i.e. venue?, unnamed 0, opponent
    # need to rename team to home in home_df and away in away_df
    # number of other things need to be changed
    # getting closer
    # and learning more each step I take