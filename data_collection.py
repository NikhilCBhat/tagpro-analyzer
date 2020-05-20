import os
import json
import requests
import tensorflow as tf
tf.enable_eager_execution()
from utils import string_date_to_attributes

def load_data_from_web():
    url = "https://tagpro.koalabeast.com/profile_rolling/53447af47e7269a515e5fe5d" 
    r = requests.get(url)
    return r.json()

def load_data_from_folder(folder_name):
    data = []
    for i in range(300):
        filename = os.path.join(folder_name, "tagpro_{}.json".format(i))
        with open(filename) as f:
            d = json.load(f)
            data.append(d)
    
    return data

def pack_dataset(features, label):
    return tf.stack(list(features.values()), axis=-1), label

def make_dataset_from_csv(file_path):
    return tf.data.experimental.make_csv_dataset(
        file_path, 
        batch_size=10,
        label_name='outcome', 
        na_value="?",
        num_epochs=1, 
        ignore_errors=True,  
        column_defaults=[0.0 for _ in range(23)],
    )

def generate_tensorflow_dataset(file_path):
    dataset = make_dataset_from_csv(file_path)
    return dataset.map(pack_dataset)

def tagpro_dict_to_tensorflow_data(tagpro_dict):
    return string_date_to_attributes(tagpro_dict["played"]) + [tagpro_dict[key] for key in [
        'gameMode', 'timePlayed', 
        'points', 'score', 'tags', 'returns', 'captures', 'grabs', 
        'drops', 'pops', 'support', 'hold', 'prevent', 'powerups', 
        'potentialPowerups', 'saved']] + [tagpro_dict["outcome"]]