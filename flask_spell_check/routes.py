import binascii
import functools
import os
import subprocess
from tempfile import NamedTemporaryFile

from flask import (current_app, flash, g, jsonify, redirect,
                   render_template, request, session, url_for, Blueprint)

bp = Blueprint('main', __name__)

db = {}


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("main.login"))

        return view(**kwargs)

    return wrapped_view

@bp.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if g.user is not None:
        response.set_cookie('username', session.get('username'), secure=False, httponly=True, samesite='Lax')

    return response

@bp.before_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    username = session.get("username")

    if username is None:
        g.user = None
    else:
        g.user = db.get(username)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    return "Hello, World"


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("uname", None)
        password = request.form.get("pword", None)
        two_factor = request.form.get("2fa", None)

        if not username:
            current_app.logger.warning("Username is null")
            success_message = "Failure - Unable to register. Please try again."
            return render_template("register.html", success_message=success_message)

        if not password:
            current_app.logger.warning("Password is null")
            success_message = "Failure - Unable to register. Password cannot be null."
            return render_template("register.html", success_message=success_message)

        user = db.get(username, None)

        if user:
            current_app.logger.warning(
                "Username in use ({username})".format(username=username)
            )
            success_message = "Failure - Unable to register. Please try again."

        if not user:
            db[username] = {"password": password, "two_factor": two_factor}
            success_message = "Success - Successfully registered."

        return render_template("register.html", success_message=success_message)

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("uname", None)
        password = request.form.get("pword", None)
        two_factor = request.form.get("2fa", None)

        if not username:
            current_app.logger.warning("Username is null")
            result_message = "Incorrect"
            return render_template("login.html", result_message=result_message)

        if not password:
            current_app.logger.warning("Password is null")
            result_message = "Incorrect"
            return render_template("login.html", result_message=result_message)

        if not two_factor:
            current_app.logger.warning("2FA is null")
            result_message = "Two-factor failure"
            return render_template("login.html", result_message=result_message)

        user = db.get(username, None)

        if not user:
            result_message = "Incorrect"
            return render_template("login.html", result_message=result_message)

        if user:
            if user["password"] != password:
                result_message = "Incorrect"
                return render_template("login.html", result_message=result_message)

            if user["two_factor"] != two_factor:
                result_message = "Two-factor failure"
                return render_template("login.html", result_message=result_message)

            session.clear()
            session["username"] = username
            result_message = "Success"
            return render_template("login.html", result_message=result_message)

    return render_template("login.html")


@bp.route("/spell_check", methods=["GET", "POST"])
@login_required
def spell_check():
    if request.method == "POST":
        text = request.form.get("inputtext", None)

        if text:
            text_file = Name()
            text_file.write(text)
            args = (
                os.path.join(app.instance_path, "a.out"),
                text_file.name,
                os.path.join(app.instance_path, "dictionary.txt"),
            )
            current_app.logger.info(args)
            result = subprocess.check_output(args)

            mispelled = result.replace("\n", ", ")[:-2]
            return render_template("index.html", mispelled=mispelled, text=text)
    return render_template("index.html")
