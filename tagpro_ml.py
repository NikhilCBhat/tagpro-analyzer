import os
import json
import pandas as pd
from utils import string_date_to_attributes
import functools
import numpy as np
np.set_printoptions(precision=3, suppress=True)
import tensorflow as tf
tf.enable_eager_execution()
from data_collection import generate_tensorflow_dataset

def generate_tagpro_dataset(folder, output_file="tagpro_ml_data.csv"):
    data = [json_to_data(os.path.join(folder, f)) for f in os.listdir(folder)]

    df = pd.DataFrame(data, columns=['second', 'minute',  'hour', 'day',  'month',  'year', 'gameMode',  'timePlayed',  'points',  'score',  'tags',  'returns',  'captures',  'grabs',  'drops',  'pops',  'support',  'hold',  'prevent', 'powerups',  'potentialPowerups',  'saved', 'outcome'])
    df["outcome"] = [int(outcome == 1) for outcome in df["outcome"]]
    df.to_csv(output_file, index=None)
    
    return output_file

def json_to_data(filepath):
    with open(filepath) as f:
        data = json.load(f)

    return string_date_to_attributes(data["played"]) + [data[key] for key in [
        'gameMode', 'timePlayed', 
        'points', 'score', 'tags', 'returns', 'captures', 'grabs', 
        'drops', 'pops', 'support', 'hold', 'prevent', 'powerups', 
        'potentialPowerups', 'saved']] + [data["outcome"]]

def show_batch(dataset):
    for batch, label in dataset.take(1):
        print("Label: {}".format(label))
        for key, value in batch.items():
            print("{:20s}: {}".format(key,value.numpy()))

if __name__ == "__main__":

    generate_tagpro_dataset("rolling_300_data")

    training_data = generate_tensorflow_dataset("tagpro_ml_data.csv")
    testing_data = generate_tensorflow_dataset("tagpro_ml_data.csv")

    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(1),
    ])

    model.compile(
        loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
        optimizer='adam',
        metrics=['accuracy'])

    model.fit(training_data, epochs=100)

    test_loss, test_accuracy = model.evaluate(testing_data)

    print('\n\nTest Loss {}, Test Accuracy {}'.format(test_loss, test_accuracy))

    predictions = model.predict(testing_data)

    for prediction, survived in zip(predictions[:10], list(testing_data)[0][1][:10]):
        prediction = tf.sigmoid(prediction).numpy()
        print("Predicted won: {:.2%}".format(prediction[0]),
                " | Actual outcome: ",
                ("Won" if bool(survived) else "Lost"))
