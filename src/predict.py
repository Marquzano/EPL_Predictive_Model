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

    new_stats_input = [[1.4, 2.012, 60.96, 14.8, 5.8, 2.2, 2.08, 46.28, 17.6, 5.2],
                       [0.8, 1.038, 41.6, 10.6, 3.2, 1.2, 1.078, 40.26, 10.6, 3.6],
                       [1.4, 1.536, 47.72, 11.8, 4, 1.6, 1.774, 56.48, 15.6, 5],
                       [0.8, 1.494, 56.88, 13, 3, 1.8, 1.814, 46.82, 13.4, 5.6],
                       [1.4, 1.122, 56.56, 13.2, 4.4, 1.4, 1.448, 48.2, 9.6, 3.2],
                       [2.4, 1.956, 66.16, 19.2, 6, 2, 1.26, 52.76, 13.8, 5.2],
                       [1.8, 1.464, 43.6, 10.6, 4.6, 1.4, 1.9, 50.56, 14.8, 4],
                       [1.2, 1.202, 46.8, 12.6, 4, 0.8, 1.12, 58.7, 14, 3.8],
                       [1, 1.192, 52.72, 12.4, 4.2, 1.8, 1.516, 36.92, 11.2, 5.6],
                       [0.4, 0.882, 40.48, 9.4, 3.4, 1, 1.002, 42.94, 12, 4]]
    
    new_team_input = [[4, 16],
                      [5, 26],
                      [7, 0],
                      [9, 17],
                      [13, 3],
                      [15, 1],
                      [19, 2],
                      [17, 6],
                      [22, 8],
                      [25, 11]]
    
    train_features_scaled, new_stats_input_scaled = scale_features(train_features, new_stats_input)

    packet = make_tensors(new_stats_input_scaled, new_team_input)

    stats_input_tensor_scaled = packet[0]
    team_input_tensor = packet[1]

    model = get_model('models/epl_1_0_4.keras')

    predictions = model.predict([team_input_tensor, stats_input_tensor_scaled])

    print(predictions)