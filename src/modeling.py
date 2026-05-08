#! /home/marquzano/miniconda3/envs/machine_learning/bin/python3
from data_transform import open_con, rolled_averages, make_matches, clean_matches, make_features_and_labels, make_cat_features, scale_features, one_hot_encode_labels
import tensorflow as tf
from keras.models import load_model
import matplotlib.pyplot as plt

# make the numpy arrays into tensors
def make_tensors(*args):
    packet = []
    for arg in args:
        tensor = tf.convert_to_tensor(arg, dtype=tf.float32)
        packet.append(tensor)

    return packet

def save_model(model, filename):
    model.save(filename)

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

    train_cat_features, validate_cat_features = make_cat_features(con)
    
    packet = make_tensors(train_features_scaled, validate_features_scaled, train_labels_encoded, validate_labels_encoded, train_cat_features, validate_cat_features)

    train_features_scaled = packet[0]
    validate_features_scaled = packet[1]
    train_labels_encoded = packet[2]
    validate_labels_encoded = packet[3]
    train_cat_features = packet[4]
    validate_cat_features = packet[5]

    # building
    

    # load model for re-training
    model = load_model('models/epl_1_0_2.keras')

    # training
    history = model.fit([train_cat_features, train_features_scaled], train_labels_encoded, epochs=50, validation_data=([validate_cat_features, validate_features_scaled], validate_labels_encoded))

    # analyzing
    training_loss = history.history['loss']
    validation_loss = history.history['val_loss']
    training_accuracy = history.history['accuracy']
    validation_accuracy = history.history['val_accuracy']

    # plot the loss
    epochs = range(1, 51)
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, training_loss, label='Training Loss')
    plt.plot(epochs, validation_loss, label='Validation Loss')
    plt.title('Model loss during training')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend()
    plt.savefig('plots/epl_1_0_2_loss.png')

    # plot the accuracy
    epochs = range(1, 51)
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, training_accuracy, label='Training Accuracy')
    plt.plot(epochs, validation_accuracy, label='Validation Accuracy')
    plt.title('Model accuracy during training')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend()
    plt.savefig('plots/epl_1_0_2_accuracy.png')

    # saving first model
    save_model(model, 'models/epl_1_0_2.keras')