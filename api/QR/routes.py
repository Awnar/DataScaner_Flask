import base64
import json
from datetime import datetime

import cv2
from PIL import Image
from flask import Blueprint, abort, jsonify, g, request, current_app
from pyzbar.pyzbar import decode
from sqlalchemy import exc

from api.common import tmpFileCreate, tmpFileDel

MOD_NAME = "QR Scaner"
api = Blueprint(MOD_NAME, __name__)


@api.route('/', methods=['GET'])
def QRgetAll():
    try:
        if g.usr is None:
            abort(403)
        time = datetime.now()
        if 'lastupdate' in request.values.dicts:
            res = current_app.config['DB'].getAllData(MOD_NAME, g.usr, request.values.dicts['lastupdate'])
        else:
            res = current_app.config['DB'].getAllData(MOD_NAME, g.usr)
        json = []
        for obj in res:
            json.append(obj.toJSON())
        return jsonify({"Data": json, "TIME": time})
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
        file = tmpFileCreate(base64.decodebytes(str.encode(Json["in_blob"])), extension=".BMP")
        data = decode(Image.open(file))
        if len(data) < 1:
            data = None
        else:
            data = data[0].data

        img = cv2.imread(file, cv2.IMREAD_COLOR)
        imgs = img.shape
        if imgs[0] > imgs[1]:
            b = int(imgs[1] / (imgs[0] / 600))
            a = 600
        else:
            a = int(imgs[0] / (imgs[1] / 600))
            b = 600

        img = cv2.resize(img, (a, b), interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(file, img)

        with open(file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        tmpFileDel(file)
        current_app.config['DB'].setData(MOD_NAME, g.usr, encoded_string, Json['in_blob_type'].strip('"'),
                                         data, "TXT", time)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/<id>', methods=['GET'])
def QRget(id):
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
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
