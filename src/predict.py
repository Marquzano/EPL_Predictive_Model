#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
from data_transform import make_features_and_labels, scale_features
from keras.models import load_model
import sqlite3
from modeling import make_tensors

def get_model(filename):
    model = load_model(filename)

    return model

if __name__ == '__main__':
    # open the sql connection
    con = sqlite3.connect('data/processed/EPL_data.db')

    train_features, validate_features, train_labels, validate_labels = make_features_and_labels(con)

    new_stats_input = [[1.4, 1.094, 55.66, 13.4, 4.4, 1.4, 1.154, 56.1, 13.6, 4.4],
                       [1.8, 1.42, 47.2, 15.8, 5.4, 1.6, 1.318, 41.38, 11.4, 4.6],
                       [1.4, 1.674, 47.5, 10.2, 3.4, 1, 1.326, 52.68, 11, 3],
                       [2, 1.614, 36.48, 12, 6.2, 0.8, 1.316, 46.72, 13.8, 3.8],
                       [1.2, 1.438, 45.66, 13.6, 5, 1.8, 1.786, 57.62, 13.6, 5.4],
                       [1, .916, 45.22, 11.2, 3.6, 0.6, 1.384, 52.5, 14.2, 2.8],
                       [1.4, 1.694, 47.54, 11.8, 4.8, 1, 1.162, 40.34, 10, 3.2],
                       [1.6, 1.98, 54.88, 16, 5, 0.8, 1.176, 43.76, 11.6, 4.2],
                       [1.6, 1.688, 50.94, 14.4, 4.2, 2.4, 2.066, 69.6, 21.2, 6.2],
                       [0.4, 1.222, 57.32, 14.6, 3.6, 0.8, 1.106, 51.14, 12.8, 5]]
    
    new_team_input = [[1, 13],
                      [16, 19],
                      [3, 7],
                      [8, 9],
                      [11, 4],
                      [26, 9],
                      [17, 25],
                      [0, 5],
                      [2, 15],
                      [6, 22]]
    
    train_features_scaled, new_stats_input_scaled = scale_features(train_features, new_stats_input)

    packet = make_tensors(new_stats_input_scaled, new_team_input)

    stats_input_tensor_scaled = packet[0]
    team_input_tensor = packet[1]

    model = get_model('models/epl_1_0_4.keras')

    predictions = model.predict([team_input_tensor, stats_input_tensor_scaled])

    print(predictions)