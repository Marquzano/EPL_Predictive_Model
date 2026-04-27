#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
import pandas as pd
import sqlite3
from sklearn.preprocessing import StandardScaler, OneHotEncoder

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
            data.append(0)
        elif value == 'L':
            data.append(1)
        else:
            data.append(2)
    
    result = pd.Series(data)
    merged_df['result'] = result.values

    return merged_df

def clean_matches(con):
    # selecting the needed features and omitting others
    # also ordering the matches in chronological order
    query = 'SELECT season, date, time, round, avg_5_gf_home, avg_5_xg_home, avg_5_poss_home, avg_5_sh_home, avg_5_sot_home, home, avg_5_gf_away, avg_5_xg_away, avg_5_poss_away, avg_5_sh_away, avg_5_sot_away, away, result FROM old_merged_matches WHERE avg_5_gf_home != -1 AND avg_5_gf_away != -1 ORDER BY date, time, round, season;'
    df = pd.read_sql(query, con=con)

    return df

def rolled_averages(con):
    # use the connection to query match_data
    # the query will run the rolled average calculations
    # as well as the formatting for the result set
    query = ('SELECT sub.date, sub.time, sub.round, sub.venue, sub.result, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_gf END AS avg_5_gf, sub.opponent, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_xg END AS avg_5_xg, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_poss END AS avg_5_poss, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_sh END AS avg_5_sh, CASE WHEN team_index <= 5 THEN -1 ELSE avg_5_sot END AS avg_5_sot, sub.team, sub.season FROM (SELECT *, ROW_NUMBER() OVER w AS team_index, AVG(gf) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_gf, AVG(xg) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_xg, AVG(poss) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_poss, AVG(sh) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_sh, AVG(sot) OVER (w ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS avg_5_sot FROM match_data WINDOW w AS (PARTITION BY team ORDER BY date, time, round, season)) sub;')

    df = pd.read_sql(query, con=con)
    return df

def make_features_and_labels(con):
    # take the feature values and append them to an array
    # the input tensor will be 1x10
    # do the same for the labels shape 1x1

    # here we pull the training and validation features data first
    query = 'SELECT avg_5_gf_home, avg_5_xg_home, avg_5_poss_home, avg_5_sh_home, avg_5_sot_home, avg_5_gf_away, avg_5_xg_away, avg_5_poss_away, avg_5_sh_away, avg_5_sot_away FROM merged_matches WHERE season in (2021, 2022, 2023, 2024);'
    train_features_df = pd.read_sql(query, con=con)
    train_features = train_features_df.to_numpy()
    query = 'SELECT avg_5_gf_home, avg_5_xg_home, avg_5_poss_home, avg_5_sh_home, avg_5_sot_home, avg_5_gf_away, avg_5_xg_away, avg_5_poss_away, avg_5_sh_away, avg_5_sot_away FROM merged_matches WHERE season in (2025);'
    validate_features_df = pd.read_sql(query, con=con)
    validate_features = validate_features_df.to_numpy()

    # next we pull the training and validation labels data
    query = 'SELECT result FROM merged_matches WHERE season in (2021, 2022, 2023, 2024)'
    train_labels_df = pd.read_sql(query, con=con)
    train_labels = train_labels_df.to_numpy()
    query = 'SELECT result FROM merged_matches WHERE season in (2025)'
    validate_labels_df = pd.read_sql(query, con=con)
    validate_labels = validate_labels_df.to_numpy()

    return train_features, validate_features, train_labels, validate_labels

def scale_features(X_train, X_validate):
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_validate_scaled = scaler.transform(X_validate)

    return X_train_scaled, X_validate_scaled

def one_hot_encode_labels(y_train, y_validate):
    encoder = OneHotEncoder(sparse_output=False)
    encoder.fit(y_train.reshape(-1,1))
    y_train_encoded = encoder.transform(y_train.reshape(-1,1))
    y_validate_encoded = encoder.transform(y_validate.reshape(-1,1))

    return y_train_encoded, y_validate_encoded

if __name__ == '__main__':
    clean_csv = 'data/processed/clean_final_matches.csv'
    db_path = 'data/processed/EPL_data.db'

    con, cur, clean_df = open_con(db_path, clean_csv, 'match_data')

    # run rolled average calculations on the match_data
    rolled_averages_df = rolled_averages(con)

    rolled_averages_df.to_csv('data/processed/rolled_averages.csv')

    rolled_averages_df.to_sql('rolled_match_data', con=con, if_exists='replace', index=False)
    
    # merging rows to have single-row unique matches
    merged_df = make_matches(rolled_averages_df)

    merged_df.to_csv('data/processed/old_merged_matches.csv')

    merged_df.to_sql('old_merged_matches', con=con, if_exists='replace', index=False)

    # cleaning up the data to necessary keys, features, and labels
    clean_merged_df = clean_matches(con)

    clean_merged_df.to_csv('data/processed/merged_matches.csv')

    clean_merged_df.to_sql('merged_matches', con=con, if_exists='replace', index=False)

    # create ndarrays of the labels and targets
    # training and validation data
    train_features, validate_features, train_labels, validate_labels = make_features_and_labels(con)

    # now we continue with sci-kit learn and create a scaler based on the training data
    # 2021-2024 seasons only
    train_features_scaled, validate_features_scaled = scale_features(train_features, validate_features)

    train_labels_encoded, validate_labels_encoded = one_hot_encode_labels(train_labels, validate_labels)

    # with that I believe we have processed all the data and can move on to modeling