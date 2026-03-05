import sqlite3
import pandas as pd

csv_file = '/home/marquzano/workspace/EPL_Predictive_Model/data/raw/final_matches.csv'

# function to manage SQL connection
def open_con():
    con = sqlite3.connect('data/raw/EPL_data.db')
    return con

def close_con():
    sqlite3_close('data/raw/EPL_data.db')

# create the connection
con = open_con()

# Go column by column checking for NULL values
# May need to dump entire columns
def fill_null(con, matches_df):
    return None

# open the csv file as a dataframe
matches_df = pd.read_csv(csv_file, na_filter=True)

# load the dataframe into SQLite
matches_df.to_sql('match_data', con=con, if_exists='replace', index=False)

# Sample code to test connection to DB
sample_query = 'SELECT distinct team FROM match_data'
transformed_df = pd.read_sql(sample_query, con=con)
print(transformed_df)

close_con()