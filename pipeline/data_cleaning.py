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
def fix_inconsistencies(df):
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
    df['team'] = df['team'].replace(team_updates)
    df['opponent'] = df['opponent'].replace(opponent_updates)
    
    return df

# make ids for each team
def make_team_ids(df, team_registry=None):
    # check if there are already registered team IDs
    if team_registry:
        # pull in the current registry of team_ids
        team_id_df = pd.read_csv(team_registry)
        # pull the current max id from the registry
        current_max_id = team_id_df['team_id'].max()
        # empty array to hold new data for rows
        new_rows = []
        # go through the current list of available teams
        for team in df['team'].unique():
            # check if a team is not registered
            if team not in team_id_df['team'].values:
                # increment the current max id
                current_max_id += 1
                # assign the id to the newest team
                new_rows.append({'team': team, 'team_id': current_max_id})
                print(f'New team assigned: {team} : {current_max_id}')
            # concatanate the new_rows into the existing registry
            if new_rows:
                # make new_rows into a df
                new_teams_df = pd.DataFrame(new_rows)
                # concatanate the old with the new
                team_id_df = pd.concat([team_id_df, new_teams_df], ignore_index=True)
        # remove unnamed: 0 column from the df
        if 'Unnamed: 0' in team_id_df.columns:
            team_id_df = team_id_df.drop(columns=['Unnamed: 0'])
        team_id_df.to_csv('data/processed/team_registry.csv')
    # here we make the registry from scratch
    else:
        # get the current set of unique teams
        unique_teams = sorted(df['team'].unique())
        # generate a dictionary with key/team_name : value/team_id
        team_to_id = {name: i for i, name in enumerate(unique_teams)}
        # make it a dataframe
        team_id_df = pd.DataFrame(team_to_id.items(), columns=['team', 'team_id'])
        # save as a csv for future reference
        team_id_df.to_csv('data/processed/team_registry.csv')
    # return the df for script use
    return team_id_df

def add_team_id_col(matches_df, team_id_df):
    # empty array to hold new row data for matches_df
    new_rows = []
    # set the index to team for lookup purposes
    team_id_df = team_id_df.set_index('team')
    for team in matches_df['team'].values:
        id = team_id_df.at[team, 'team_id']
        new_rows.append(id)
    matches_df['team_id'] = new_rows
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

    # 'data/processed/team_registry.csv'
    team_id_df = make_team_ids(cleaned_df, 'data/processed/team_registry.csv')

    # add the team_id columns to the current matches_df
    matches_df = add_team_id_col(cleaned_df, team_id_df)

    # variables to create connection using new db and cleaned data
    clean_db = 'data/processed/EPL_data.db'
    new_csv = 'data/processed/clean_final_matches.csv'

    make_csv(matches_df, new_csv)

    close_con(con)

    # create connection to new db
    con, cur, matches_df = open_con(clean_db, new_csv, 'match_data')

    check_matches(cur)

    # add team_registry table
    create_table(con, team_id_df, 'team_registry')

    # review notes to determine output we need
    # our input will be the new EPL_data.db/clean_file_matches.csv
    # need to transform data

    close_con(con)