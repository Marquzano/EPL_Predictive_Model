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

    new_stats_input = [[1.6, 1.332, 57.7, 14.8, 5, 0.2, 1.436, 58.74, 17.6, 3.6],
                       [1.6, 1.626, 54.78, 12.8, 4.8, 1, 0.932, 48.36, 11.6, 3.8],
                       [0.6, 1.272, 50.96, 13.6, 2.4, 1.8, 2.122, 52.16, 14.8, 3.8],
                       [1.4, 1.412, 46.54, 12.8, 4.4, 2, 1.354, 45.66, 14.4, 5.4],
                       [2.2, 1.868, 67.64, 19.8, 6, 1.4, 1.912, 48.8, 12, 3.8],
                       [0.6, 0.89, 46.8, 9.4, 3.6, 1.8, 1.374, 52.34, 12.8, 4.4],
                       [1, 1.326, 54.44, 9.6, 2.2, 1.8, 1.454, 37.06, 11.4, 5.8],
                       [2.2, 1.336, 42.4, 10, 4.2, 1.4, 1.716, 47.48, 11, 4.2],
                       [1, 1.054, 42.22, 10, 3.4, 1.6, 2.068, 50.44, 14.8, 4.8],
                       [1, 1.07, 48.22, 12.2, 5.6, 1.6, 1.734, 48.28, 14.8, 5.4],
                       [2.2, 1.868, 67.64, 19.8, 6, 1, 1.326, 54.44, 9.6, 2.2]]
    
    new_team_input = [[13, 6],
                      [4, 26],
                      [9, 2],
                      [9, 16],
                      [15, 3],
                      [5, 1],
                      [7, 8],
                      [19, 17],
                      [25, 0],
                      [22, 11],
                      [15, 7]]
    
    train_features_scaled, new_stats_input_scaled = scale_features(train_features, new_stats_input)

    packet = make_tensors(new_stats_input_scaled, new_team_input)

    stats_input_tensor_scaled = packet[0]
    team_input_tensor = packet[1]

    model = get_model('models/epl_1_0_2.keras')

    predictions = model.predict([team_input_tensor, stats_input_tensor_scaled])

    print(predictions)