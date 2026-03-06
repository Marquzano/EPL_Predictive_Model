#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import sqlite3
import pandas as pd

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

# Fill in for NULL values
def fill_null(con, cur, matches_df):
    return None

def check_raw_matches(cur, matches_df):
    # checking the structure of the table
    cur.execute('PRAGMA table_info(match_data);')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT date FROM match_data;')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT time FROM match_data;')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT comp FROM match_data;')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT round FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT day FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT venue FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Target, no nulls
    cur.execute('SELECT DISTINCT result FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT gf FROM match_data')
    print(cur.fetchall())
    
    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT ga FROM match_data')
    print(cur.fetchall())
    
    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT opponent FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT xg FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT xga FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT poss FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT attendance FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT captain FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed, (Feature?), no nulls, do see some unrecognized characters
    cur.execute('SELECT DISTINCT formation FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed, (Feature?), no nulls
    cur.execute('SELECT DISTINCT "opp formation" FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT referee FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT "match report" FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT notes FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT sh FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT sot FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT dist FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT fk FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT pk FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # not needed
    cur.execute('SELECT DISTINCT pkatt FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Feature, no nulls
    cur.execute('SELECT DISTINCT team FROM match_data')
    print(cur.fetchall())

    print('\n\n\n\n\n')
    # Key, no nulls
    cur.execute('SELECT DISTINCT season FROM match_data')
    print(cur.fetchall())

# main method where logic and transformation take place
if __name__ == '__main__':
    # define csv file
    csv_file = '/home/marquzano/workspace/EPL_Predictive_Model/data/raw/final_matches.csv'

    # create the connection
    con, cur = open_con()

    # Sample code to test connection to DB
    # sample_query = 'SELECT distinct team FROM match_data
    # transformed_df = pd.read_sql(sample_query, con=con)
    # print(transformed_df)

    # open the csv file as a dataframe
    matches_df = pd.read_csv(csv_file, na_filter=True)

    # load the dataframe into SQLite
    matches_df.to_sql('match_data', con=con, if_exists='replace', index=False)

    # going through column by column
    check_raw_matches(cur, matches_df)

    # removes unnecessary columns for modeling
    matches_df = remove_columns(con)
    print(matches_df['notes'])
    print('\n\n\n\n\n')

    # check what remains
    # it does not check what remains since you are only querying the DB here
    # not the transformed df
    # check_raw_matches(cur, matches_df)

    # need to clean up team names (there are inconsistencies)


    close_con(con)