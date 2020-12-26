import secrets
from datetime import timedelta, datetime
from hashlib import sha512, sha256

from flask import jsonify, current_app, request, abort, g

validity_deltatime = timedelta(hours=1)


def home():
    DATA = {
        "name": {
            0: 'Skaner QR'
        },
        "url": {
            0: '/QR'
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
            abort(403)
        return jsonify({"Authorization": hash})


def logout():
    if g.usr is not None:
        current_app.config['DB'].Logout(request.headers['Authorization'])


def register():
    if g.usr is not None:
        abort(405)
    if not ('name' and 'pass') in request.form:
        abort(406)

    tmp = current_app.config['DB'].checkUser(request.form['name'].strip("    \""))
    if tmp is not None:
        return jsonify({"ERROR": "Taki użytkownik już istnieje"})

    llen = 255 - len(request.form['name'].encode())
    if llen < 0:
        llen = 0
    hash = sha512(secrets.token_urlsafe(llen).encode() + request.form['name'].encode()).hexdigest()
    meta = {"User-Agent": request.headers["User-Agent"], "IP": request.remote_addr}

    current_app.config['DB'].RegisterAndLogin(request.form['name'].strip("    \""),
                                              sha256(request.form['pass'].strip("    \"").encode('utf-8')).hexdigest(),
                                              hash, meta)

    return jsonify({"Authorization": hash})
