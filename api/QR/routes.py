import base64
import json
from datetime import datetime

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
        return jsonify()
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

        file = tmpFileCreate(base64.decodebytes(str.encode(Json["in_blob"])))
        data = decode(Image.open(file))
        if len(data) < 1:
            data = None
        else:
            data = data[0].data
        tmpFileDel(file)
        time = datetime.now()
        current_app.config['DB'].setData(MOD_NAME, g.usr, str.encode(Json['in_blob']), Json['in_blob_type'].strip('"'),
                                         data, "TXT", time)

        return jsonify({
            'in_blob': Json['in_blob'],
            'in_blob_type': Json['in_blob_type'],
            'out_blob': data,
            'out_blob_type': 'txt',
            'crete': time,
            'update': time
        })
    except exc.SQLAlchemyError as e:
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
