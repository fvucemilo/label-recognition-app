import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow import keras
import numpy as np
import json
import requests

SIZE=(200, 200)
MODEL_URI='https://wine-model-tfs.herokuapp.com/v1/models/wine_model:predict'
CLASSES = ['b1', 'b10', 'b11', 'b12', 'b13', 'b14', 'b15', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9']

def get_prediction(image_path):
    image = keras.preprocessing.image.load_img(image_path, target_size=SIZE, color_mode='grayscale')
    image = keras.preprocessing.image.img_to_array(image)
    image = np.expand_dims(image, axis=0)

    data = json.dumps({'signature_name': 'serving_default', 'instances': image.tolist()})
    headers = {'content-type': 'application/json'}

    response = requests.post(MODEL_URI, data=data.encode('utf-8'), headers=headers)
    response.raise_for_status()

    predictions = json.loads(response.text)['predictions']
    score = tf.nn.softmax(predictions[0])
    prediction = {'class_name': CLASSES[np.argmax(score)], 'score': round(100 * np.max(score), 2)}
    return prediction
