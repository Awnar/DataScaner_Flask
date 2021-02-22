import base64
import json
import time
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

        t = time.time()
        if 'lastupdate' in request.values:
            res = current_app.config['DB'].getAllData(MOD_NAME, g.usr, request.values['lastupdate'])
        else:
            res = current_app.config['DB'].getAllData(MOD_NAME, g.usr)
        j = []
        for obj in res:
            j.append(obj.id)
        return jsonify({"Data": j, "TIME": t})
        # def generate():
        #    yield '{"TIME":'+str(t)+',"Data":'
        #    for row in res:
        #        z = row.toJSON()
        #        zz = json.dumps(z, indent=4, sort_keys=True, default=str)
        #        yield zz + ','
        #    yield '}'
        # return Response(generate(), mimetype='text')
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

        #img = cv2.imread(file, cv2.IMREAD_COLOR)
        #if img.shape[0] > img.shape[1]:
        #   b = int(200 * img.shape[1] / img.shape[0])
        #   a = 200
        #else:
        #   a = int(200 * img.shape[0] / img.shape[1])
        #   b = 200
        #img = cv2.resize(img, (a, b))#, interpolation=cv2.INTER_LANCZOS4)
        #cv2.imwrite(file, img)

        with open(file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        tmpFileDel(file)
        current_app.config['DB'].setData(MOD_NAME, g.usr, encoded_string, Json['in_blob_type'], data, "TXT", time)
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
