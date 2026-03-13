#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import sqlite3
import pandas as pd
from check_data import check_matches, check_raw_matches

# Create/return DB connection objects
def open_con(db_path, csv_path, table_name):
    # create the connection
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # open csv file as a dataframe
    df = pd.read_csv(csv_path, na_filter=True)
    # load the dataframe as a table
    df.to_sql(table_name, con=con, if_exists='replace', index=False)
    
    return con, cur, df

# creates new table in DB
def create_table(con, df, table_name):
    df.to_sql(table_name, con=con, if_exists='replace', index=False)

# Closes DB connection
def close_con(con):
    con.close()

# create csv file from dataframe
def make_csv(df, filepath):
    df.to_csv(filepath)

# removes unnecessary columns for modeling
def remove_columns(con):
    # add only necessary columns in the query
    query = 'SELECT date, time, round, venue, result, gf, ga, opponent, xg, xga, poss, sh, sot, team, season FROM match_data;'
    new_matches_df = pd.read_sql(query, con=con)
    return new_matches_df

# fixes inconsistencies between opponent and team columns
def fix_inconsistencies(matches_df):
    # make mapping dictionaries for opponent and team columns
    team_updates = {
        "Brighton And Hove Albion": "Brighton",
        "West Bromwich Albion": "West Brom",
        "West Ham United": "West Ham"
    }

    opponent_updates = {
        "Manchester Utd": "Manchester United",
        "Newcastle Utd": "Newcastle United",
        "Nott'ham Forest": "Nottingham Forest",
        "Sheffield Utd": "Sheffield United",
        "Tottenham": "Tottenham Hotspur",
        "Wolves": "Wolverhampton Wanderers"
    }

    # update df accordingly
    matches_df['team'] = matches_df['team'].replace(team_updates)
    matches_df['opponent'] = matches_df['opponent'].replace(opponent_updates)
    
    return matches_df

# main method where logic and transformation take place
if __name__ == '__main__':
    # define raw csv file
    raw_file = 'data/raw/final_matches.csv'
    raw_db = 'data/raw/Raw_EPL_data.db'

    # create the connection
    con, cur, matches_df = open_con(raw_db, raw_file, 'match_data')

    # going through column by column
    # check_raw_matches(cur)

    # removes unnecessary columns for modeling
    matches_df = remove_columns(con)

    # need to clean up team names (there are inconsistencies)
    cleaned_df = fix_inconsistencies(matches_df)

    # variables to create connection using new db and cleaned data
    clean_db = 'data/processed/EPL_data.db'
    new_csv = 'data/processed/clean_final_matches.csv'

    make_csv(cleaned_df, new_csv)

    close_con(con)

    # create connection to new db
    con, cur, matches_df = open_con(clean_db, new_csv, 'match_data')

    check_matches(cur)

    # review notes to determine output we need
    # our input will be the new EPL_data.db/clean_file_matches.csv
    # need to transform data

    close_con(con)