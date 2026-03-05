import sqlite3
import pandas as pd

# function to create/return DB connection
def open_con():
    con = sqlite3.connect('data/raw/EPL_data.db')
    cur = con.cursor()
    return con, cur

# closes DB connection
def close_con(con):
    con.close()

# Go column by column checking for NULL values
# May need to dump entire columns
def fill_null(con, cur, matches_df):
    return None

def check_raw_matches(cur, matches_df):
    cur.execute('PRAGMA table_info(match_data);')
    print(cur.fetchall())
    print('\n\n\n\n\n')
    cur.execute('SELECT DISTINCT date FROM match_data;')
    print(cur.fetchall())
    print('\n\nSame Result Set but utilizing Pandas\n\n')
    distinct_dates = pd.read_sql('SELECT DISTINCT date FROM match_data;', con=con)
    print(distinct_dates)

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

    check_raw_matches(cur, matches_df)

    close_con(con)