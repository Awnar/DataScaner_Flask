import secrets

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

import model

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3308/qr?charset=utf8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
app.config['DB'] = model.SQLClass(db)()

import api
from api.QR import api as api_alfa

app.register_blueprint(api_alfa, url_prefix='/QR')


@app.route('/')
def index():
    return api.home()


@app.before_request
def require_authorization():
    try:
        return api.require_authorization()
    except exc.SQLAlchemyError:
        return jsonify({"ERROR": "Błąd autoryzacji"})


@app.route('/login', methods=['POST'])
def login():
    try:
        return api.login()
    except exc.SQLAlchemyError:
        return jsonify({"ERROR": "Błąd logowania"})


@app.route('/logout')
def logout():
    try:
        return api.logout()
    except exc.SQLAlchemyError:
        return jsonify({"ERROR": "Błąd zamykania sesji"})


@app.route('/register', methods=['POST'])
def register():
    try:
        return api.register()
    except exc.SQLAlchemyError:
        return jsonify({"ERROR": "Błąd rejestracji"})


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0')
