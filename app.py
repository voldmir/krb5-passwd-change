
#import sys
#import traceback
# from pprint import pprint
import os
from datetime import datetime, date, timedelta
from lib.base import Base
from lib.krb5creds import Krb5Creds
from flask import jsonify, abort, session, request, render_template
import logging

app = Base(__name__, path_app=os.path.abspath(os.path.dirname(__file__)))

# print(app.secret_key)


@app.route('/api/username', methods=['POST', 'PATCH', 'PUT'])
def init_creds_password():
    if request.method == 'POST':
        if 'username' in session and 'password' in session:
            return jsonify((0, "Ok"))
        else:
            session['username'] = request.form.get('username')
            session['password'] = request.form.get('password')

        return jsonify(Krb5Creds(session['username'], session['password']).init_creds_password())

    if request.method == 'PATCH':
        if 'username' in session and 'password' in session:
            ret = Krb5Creds(session['username'], session['password']).change_password(
                request.form.get('password_new'))
            session.pop('username', None)
            session.pop('password', None)
            return jsonify(ret)
        else:
            return jsonify((-1, "err"))

    if request.method == 'PUT':
        if 'username' in session and 'password' in session:
            ret = Krb5Creds(session['username'], session['password']).set_password(
                request.form.get('password_new'))
            session.pop('username', None)
            session.pop('password', None)
            return jsonify(ret)
        else:
            return jsonify((-1, "err"))


@app.route('/', methods=['GET'])
def root_page():
    return render_template('index.html', utc_dt=datetime.utcnow())


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
