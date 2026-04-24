#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
from data_transform import open_con, rolled_averages, make_matches, clean_matches, make_labels_and_targets, scale_labels, one_hot_encode_targets
import tensorflow as tf

# make the numpy arrays into tensors
def make_tensors(*args):
    packet = []
    for arg in args:
        tensor = tf.convert_to_tensor(arg, dtype=tf.float32)
        packet.append(tensor)

    return packet

def make_model():
    pass

def load_model():
    pass

def save_model():
    pass

if __name__ == '__main__':
    # bring in the data from data_transform
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
    train_labels, validate_labels, train_targets, validate_targets = make_labels_and_targets(con)

    # now we continue with sci-kit learn and create a scaler based on the training data
    # 2021-2024 seasons only
    train_labels_scaled, validate_labels_scaled = scale_labels(train_labels, validate_labels)

    train_targets_encoded, validate_targets_encoded = one_hot_encode_targets(train_targets, validate_targets)
    
    packet = make_tensors(train_labels_scaled, validate_labels_scaled, train_targets_encoded, validate_targets_encoded)

    train_labels_scaled = packet[0]
    validate_labels_scaled = packet[1]
    train_targets_encoded = packet[2]
    validate_targets_encoded = packet[3]

