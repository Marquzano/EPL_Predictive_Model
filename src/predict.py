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

    new_input = [[1.4, 1.57, 46.8, 13.2, 4.4, 0.4, 0.9, 43.2, 9.4, 3.2],
                 [1, 1.69, 50.2, 11.6, 3.4, 1.4, 1.1, 40.7, 9.4, 3.2],
                 [0.8, 1.28, 52, 11, 3.6, 2, 1.75, 51.8, 13, 5.8],
                 [0.8, 0.73, 45, 10, 2.8, 1.2, 1.42, 50.3, 13.6, 4.8],
                 [1.2, 1.52, 48.7, 13.4, 3.8, 0.8, 1.43, 49.5, 14.2, 3.4],
                 [1.6, 2.04, 34.2, 15, 4.2, 1.2, 1.6, 53.72, 11, 3.4],
                 [1.8, 1.16, 47.18, 13, 5.4, 1.8, 1.38, 55.82, 14, 4.6],
                 [1.6, 1.496, 55.6, 13.8, 4.4, 0.8, 1.056, 49, 12.4, 5],
                 [0, 1.08, 54.76, 14.6, 2.6, 2.6, 1.146, 43.58, 10.8, 4.6],
                 [1.4, 1.2, 43.36, 10.8, 5.2, 1.8, 2.232, 65.64, 21.2, 7]]
    
    train_features_scaled, new_input_scaled = scale_features(train_features, new_input)

    packet = make_tensors(train_features_scaled, new_input_scaled)

    input_tensor_scaled = packet[1]

    model = get_model('models/epl_0_0_2.keras')

    predictions = model.predict(input_tensor_scaled)

    print(predictions)