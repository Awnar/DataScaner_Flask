import base64
import json
import time
from datetime import datetime

from PIL import Image
from flask import Blueprint, abort, jsonify, g, request, current_app
from sqlalchemy import exc

from api.common import tmpFileCreate, tmpFileDel


import os
import tensorflow as tf
import tensorflow_hub as hub
# Load compressed models from tensorflow_hub
os.environ['TFHUB_MODEL_LOAD_FORMAT'] = 'COMPRESSED'
#import IPython.display as display
#import matplotlib.pyplot as plt
import matplotlib as mpl
#mpl.rcParams['figure.figsize'] = (12,12)
#mpl.rcParams['axes.grid'] = False
import numpy as np
import functools

MOD_NAME = "AI"
api = Blueprint(MOD_NAME, __name__)

hub_model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
#style_path = tf.keras.utils.get_file('kandinsky5.jpg','https://storage.googleapis.com/download.tensorflow.org/example_images/Vassily_Kandinsky%2C_1913_-_Composition_7.jpg')
style_path = tf.keras.utils.get_file('kandinsky7.jpg','https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Great_Wave_off_Kanagawa_restored.jpg/1200px-Great_Wave_off_Kanagawa_restored.jpg')

def tensor_to_image(tensor):
  tensor = tensor*255
  tensor = np.array(tensor, dtype=np.uint8)
  if np.ndim(tensor)>3:
    assert tensor.shape[0] == 1
    tensor = tensor[0]
  return Image.fromarray(tensor)

def load_img(path_to_img):
  max_dim = 300
  img = tf.io.read_file(path_to_img)
  img = tf.image.decode_image(img, channels=3)
  img = tf.image.convert_image_dtype(img, tf.float32)

  shape = tf.cast(tf.shape(img)[:-1], tf.float32)
  long_dim = max(shape)
  scale = max_dim / long_dim

  new_shape = tf.cast(shape * scale, tf.int32)

  img = tf.image.resize(img, new_shape)
  img = img[tf.newaxis, :]
  return img


@api.route('/', methods=['GET'])
def QRgetAll():
    try:
        if g.usr is None:
            abort(403)

        t = time.time()
        if 'lastupdate' in request.values:
            res = current_app.config['DB'].getAllData(MOD_NAME, g.usr, request.values['lastupdate'])
        else:
            res = current_app.config['DB'].getAllData(MOD_NAME, g.usr)
        j = []
        for obj in res:
            j.append(obj.id)
        return jsonify({"Data": j, "TIME": t})

    except exc.SQLAlchemyError:
        abort(500)


@api.route('/', methods=['POST'])
def QRpost():
    try:
        if g.usr is None:
            abort(403)
        if 'data' not in request.form:
            abort(406)

        Json = json.loads(request.form['data'])
        if 'in_blob' and 'in_blob_type' not in Json:
            abort(406)

        time = datetime.now()
        file = tmpFileCreate(base64.decodebytes(str.encode(Json["in_blob"])), extension=".JPG")

        content_image = load_img(file)
        style_image = load_img(style_path)

        tmpFileDel(file)

        stylized_image = hub_model(tf.constant(content_image), tf.constant(style_image))[0]
        img = tensor_to_image(stylized_image)

        img.save(file,optimize=True,quality=1)

        with open(file, "rb") as image_file:
           encoded_string = base64.b64encode(image_file.read())

        tmpFileDel(file)

        current_app.config['DB'].setData(MOD_NAME, g.usr, str.encode(Json["in_blob"]), Json['in_blob_type'], encoded_string, "IMG", time)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/<id>', methods=['GET'])
def QRget(id):
    try:
        if g.usr is None:
            abort(403)

        res = current_app.config['DB'].getData(MOD_NAME, id, g.usr)
        return jsonify(res.toJSON())
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/<id>', methods=['DELETE'])
def QRdelete(id):
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/<id>', methods=['PUT'])
def QRput(id):
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)
