from flask import Blueprint, abort, jsonify, g
from sqlalchemy import exc

MOD_NAME = "Template"
api = Blueprint('MOD_NAME', __name__)


@api.route('/', methods=['GET'])
def DatagetAll():
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/', methods=['POST'])
def Datapost():
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/<id>', methods=['GET'])
def Dataget(id):
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/<id>', methods=['DELETE'])
def Datadelete(id):
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)


@api.route('/<id>', methods=['PUT'])
def Dataput(id):
    try:
        if g.usr is None:
            abort(403)
        return jsonify()
    except exc.SQLAlchemyError:
        abort(500)
