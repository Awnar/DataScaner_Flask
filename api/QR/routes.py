from flask import Blueprint, abort, jsonify, g
from sqlalchemy import exc

api = Blueprint('api', __name__)

MOD_NAME = "QR Scaner"


@api.route('/QR', methods=['GET'])
def QRgetAll():
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/QR', methods=['POST'])
def QRpost():
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/QR/<id>', methods=['GET'])
def QRget(id):
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/QR/<id>', methods=['DELETE'])
def QRdelete(id):
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/QR/<id>', methods=['PUT'])
def QRput(id):
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)
