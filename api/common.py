import os
import secrets
from datetime import timedelta, datetime
from hashlib import sha512, sha256

from flask import jsonify, current_app, request, abort, g

validity_deltatime = timedelta(hours=1)


def home():
    DATA = {
        'endpoints': {
            0: {
                'name': 'Template'
                #'url': '/Template'
            },
            1: {
                'name': 'Bar Skaner',
                'url': '/QR'
            },
            2: {
                'name': 'AI',
                'url': '/AI'
            }
        }
    }
    return jsonify(DATA)


def require_authorization():
    g.usr = None
    if 'Authorization' in request.headers and request.headers['Authorization'] is not None:
        dbtoken = current_app.config['DB'].getToken(token=request.headers['Authorization'])
        if dbtoken:
            if dbtoken.validity_time > datetime.now():
                current_app.config['DB'].updateToken(request.headers['Authorization'])
                g.usr = dbtoken.user_id


def login():
    if g.usr is None:
        if not ('name' and 'pass') in request.form:
            abort(406)
        llen = 255 - len(request.form['name'].strip("    \"").encode())
        if llen < 0:
            llen = 0
        hash = sha512(secrets.token_urlsafe(llen).encode() + request.form['name'].encode()).hexdigest()
        meta = {"User-Agent": request.headers["User-Agent"], "IP": request.remote_addr}
        user = current_app.config['DB'].Login(request.form['name'].strip("    \""),
                                              sha256(request.form['pass'].strip("    \"").encode('utf-8')).hexdigest(),
                                              hash, meta)
        if user is None:
            # abort(403)
            return jsonify({"ERROR": "Taki użytkownik nie istnieje"})
        return jsonify({"Authorization": hash})


def logout():
    if g.usr is not None:
        current_app.config['DB'].Logout(request.headers['Authorization'])
        return {}, 200
    return {}, 401


def register():
    if g.usr is not None:
        abort(405)
    if not ('name' and 'pass') in request.form:
        abort(406)

    tmp = current_app.config['DB'].checkUser(request.form['name'].strip("    \""))
    if len(tmp) != 0:
        return jsonify({"ERROR": "Taki użytkownik już istnieje"})

    llen = 255 - len(request.form['name'].encode())
    if llen < 0:
        llen = 0
    hash = sha512(secrets.token_urlsafe(llen).encode() + request.form['name'].encode()).hexdigest()
    meta = {"User-Agent": request.headers["User-Agent"], "IP": request.remote_addr}

    user = current_app.config['DB'].RegisterAndLogin(request.form['name'].strip("    \""),
                                                     sha256(request.form['pass'].strip("    \"").encode(
                                                         'utf-8')).hexdigest(),
                                                     hash, meta)
    if user is None:
        # abort(403)
        return jsonify({"ERROR": "Dodanie użytkownika nie udało się"})
    return jsonify({"Authorization": hash})


def tmpFileCreate(data, type="IMG", writemode="wb", extension=""):
    path = os.path.join('tmp', type)
    if not os.path.exists(path):
        os.makedirs(path)

    file_path = os.path.join(path, secrets.token_urlsafe(12) + extension)
    f = open(file_path, writemode)
    f.write(data)
    f.close()

    return file_path


def tmpFileDel(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
