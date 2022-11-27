# import sys
# import traceback
# from pprint import pprint
# from datetime import datetime, date, timedelta
import json
from lib.base import Base
from flask import jsonify, abort, session, request, render_template, redirect
import os


app = Base(__name__)


@app.route("/action/auth", methods=["POST"])
def creds_password_post():
    if "username" in session and "password" in session:
        pass
    else:
        if (
            (not request.form.get("captcha"))
            and (not request.form.get("username"))
            and (not request.form.get("password"))
        ):
            session["mess_prev"] = "Не заполнены обязательные поля."
            return redirect("/")

        if ("captcha_answer" not in session) or (
            request.form.get("captcha") != session["captcha_answer"]
        ):
            session["mess_prev"] = "Не верно введена капча."
            session.pop("captcha_answer", None)
            return redirect("/")

        username = app.upn_replace(request.form.get("username"))
        ret = app.krb5.init_creds_password(
            username,
            request.form.get("password"),
            (
                request.environ.get("HTTP_X_FORWARDED_FOR")
                or request.environ["REMOTE_ADDR"]
            ),
        )
        session["mess_prev"] = ret[1]

        if ret[0] in [0, 2]:
            session["username"] = username
            session["password"] = request.form.get("password")
            session["krb5code"] = ret[0]

    return redirect("/")


@app.route("/action/change_password", methods=["POST"])
def creds_password_patch():
    #    print(json.dumps(dict(session)))
    if (
        "username" in session
        and "password" in session
        and "method" in request.form
        and "password_new" in request.form
    ):

        session["mess_prev"] = (
            app.krb5.set_password(
                session["username"],
                request.form.get("password_new"),
                (
                    request.environ.get("HTTP_X_FORWARDED_FOR")
                    or request.environ["REMOTE_ADDR"]
                ),
            )
            if request.form.get("method") == "put"
            else app.krb5.change_password(
                session["username"],
                session["password"],
                request.form.get("password_new"),
                (
                    request.environ.get("HTTP_X_FORWARDED_FOR")
                    or request.environ["REMOTE_ADDR"]
                ),
            )
        )

    logout()

    return redirect("/")


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    session.pop("password", None)
    session.pop("krb5code", None)
    session.pop("captcha_answer", None)
    return redirect("/")


@app.route("/", methods=["GET"])
def root_page():
    if "username" in session and "password" in session and "krb5code" in session:
        return render_template(
            "edit.html",
            method="put" if session["krb5code"] == 0 else "patch",
            mess=session.pop("mess_prev", ""),
        )
    else:
        return render_template(
            "login.html",
            mess=session.pop("mess_prev", ""),
            captcha=app.captcha_generate(),
        )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
