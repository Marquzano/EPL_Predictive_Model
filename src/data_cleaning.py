#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import sqlite3
import pandas as pd
from check_data import check_matches, check_raw_matches

# Create/return DB connection objects
def open_con():
    con = sqlite3.connect('data/raw/EPL_data.db')
    cur = con.cursor()
    return con, cur

# Closes DB connection
def close_con(con):
    con.close()

# removes unnecessary columns for modeling
def remove_columns(con):
    # add only necessary columns in the query
    query = 'SELECT date, time, round, venue, result, gf, ga, opponent, xg, xga, poss, sh, sot, team, season FROM match_data;'
    new_matches_df = pd.read_sql(query, con=con)
    return new_matches_df

# fixes inconsistencies between opponent and team columns
# change team names for Brighton And Hove Albion, West Bromwich Albion, West ham United
# change opponent names for Machester Utd, Newcastle Utd, Nott'ham Forest, Sheffield Utd, Tottenham, Wolves
def fix_inconsistencies(matches_df):
    # messing around learning how to transform using DataFrames
    for k, v in (matches_df.items()):
        print('\n\n\n')
        print(f'{k}: {v}')
        print('\n\n\n')
    
    return None

# main method where logic and transformation take place
if __name__ == '__main__':
    # define csv file
    csv_file = '/home/marquzano/workspace/EPL_Predictive_Model/data/raw/final_matches.csv'

    # create the connection
    con, cur = open_con()

    # open the csv file as a dataframe
    matches_df = pd.read_csv(csv_file, na_filter=True)

    # load the dataframe into SQLite
    matches_df.to_sql('match_data', con=con, if_exists='replace', index=False)

    # going through column by column
    check_raw_matches(cur, matches_df)

    # go through new data set
    check_matches(cur, matches_df)

    # removes unnecessary columns for modeling
    matches_df = remove_columns(con)

    # need to clean up team names (there are inconsistencies)
    matches_df = fix_inconsistencies(matches_df)

    close_con(con)