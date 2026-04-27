#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
from data_transform import open_con, rolled_averages, make_matches, clean_matches, make_features_and_labels, scale_features, one_hot_encode_labels
import tensorflow as tf

# make the numpy arrays into tensors
def make_tensors(*args):
    packet = []
    for arg in args:
        tensor = tf.convert_to_tensor(arg, dtype=tf.float32)
        packet.append(tensor)

    return packet

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
    train_features, validate_features, train_labels, validate_labels = make_features_and_labels(con)

    # now we continue with sci-kit learn and create a scaler based on the training data
    # 2021-2024 seasons only
    train_features_scaled, validate_features_scaled = scale_features(train_features, validate_features)

    train_labels_encoded, validate_labels_encoded = one_hot_encode_labels(train_labels, validate_labels)
    
    packet = make_tensors(train_features_scaled, validate_features_scaled, train_labels_encoded, validate_labels_encoded)

    train_features_scaled = packet[0]
    validate_features_scaled = packet[1]
    train_labels_encoded = packet[2]
    validate_labels_encoded = packet[3]

    model1 = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(1,10)),
        tf.keras.layers.Dense(units=10, activation='relu'),
        tf.keras.layers.Dense(units=1, activation='softmax')
    ])

    model1.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy', 'precision'])

    model1.fit(train_features_scaled, train_labels_encoded, epochs=100)