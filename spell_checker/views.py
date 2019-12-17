from datetime import datetime as dt
from tempfile import NamedTemporaryFile
from spell_checker import db, login_manager
from flask import (
    abort,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    current_app,
    Blueprint,
)
import os
import subprocess
from flask_login import current_user, login_user, logout_user, login_required

from spell_checker.forms import (
    RegisterForm,
    LoginForm,
    SpellCheckForm,
    SpellCheckQueryHistoryForm,
    LoginHistoryForm,
)
from spell_checker.models import Users, AuthHistory, SpellCheckQuery

spell_checker = Blueprint("spell_checker", __name__, template_folder="templates")

@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).one_or_none()

@spell_checker.route("/")
@login_required
def index():
    return render_template("index.html")


@spell_checker.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("spell_checker.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = Users(
            username=form.username.data,
            password=form.password.data,
            two_factor=form.two_factor.data,
        )

        db.session.add(user)
        db.session.commit()

        flash("success", category='success')

        return redirect(url_for("spell_checker.login"))

    return render_template("register.html", form=form)


@spell_checker.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("spell_checker.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).one_or_none()

        if user is None or not user.check_password(form.password.data):
            flash("Incorrect username or password", category="result")
            return redirect(url_for("spell_checker.login"))

        if user.two_factor is not None and not user.check_two_factor(
            form.two_factor.data
        ):
            flash("Failure: Two-factor authentication", category="result")
            return redirect(url_for("spell_checker.login"))

        login_user(user)

        flash("success", category="result")

        auth_event = AuthHistory(login_timestamp=dt.utcnow(), user_id=current_user.id)

        db.session.add(auth_event)
        db.session.commit()

        return redirect(url_for("spell_checker.index"))

    return render_template("login.html", form=form)


@spell_checker.route("/logout")
def logout():
    auth_event = (
        AuthHistory.query.filter_by(user_id=current_user.id)
        .order_by(AuthHistory.id.desc())
        .first()
    )
    auth_event.logout_timestamp = dt.utcnow()
    db.session.add(auth_event)
    db.session.commit()

    logout_user()

    return redirect(url_for("spell_checker.index"))


@spell_checker.route("/spell_check", methods=["GET", "POST"])
@login_required
def spell_check():
    form = SpellCheckForm()
    if form.validate_on_submit():

        tmp_file = NamedTemporaryFile()
        tmp_file.write(form.input.data.encode())
        args = (
            os.path.join(current_app.instance_path, "a.out"),
            tmp_file.name,
            os.path.join(current_app.instance_path, "dictionary.txt"),
        )

        result = subprocess.check_output(args).decode("UTF-8")

        result = result.replace("\n", ", ")[:-2]

        spell_check_query = SpellCheckQuery(
            text=form.input.data, result=result, user_id=current_user.id
        )
        db.session.add(spell_check_query)
        db.session.commit()

        return render_template(
            "spell_check.html", text=form.input.data.encode(), result=result
        )
    return render_template("spell_check.html", form=form)


@spell_checker.route("/history", methods=["GET", "POST"])
@spell_checker.route(
    "/history/query<int:spell_check_query_id>", methods=["GET", "POST"]
)
@login_required
def history(spell_check_query_id=None):
    if current_user.is_admin:
        if spell_check_query_id:
            spell_check_query = SpellCheckQuery.query.filter_by(
                id=spell_check_query_id
            ).one_or_none()
            if spell_check_query:
                return render_template(
                    "single_query_history.html", spell_check_query=spell_check_query
                )
            else:
                return abort(404)
        else:
            form = SpellCheckQueryHistoryForm()
            if form.validate_on_submit():
                u = Users.query.filter_by(username=form.username.data).one_or_none()
                if u:
                    queries = SpellCheckQuery.query.filter_by(user_id=u.id).all()
                    return render_template(
                        "user_query_history.html", queries=queries, user=u, form=form
                    )
                else:
                    return abort(404)
            return render_template("query_history.html", form=form)
    else:
        if spell_check_query_id:
            spell_check_query = SpellCheckQuery.query.filter_by(
                id=spell_check_query_id, user_id=current_user.id
            ).one_or_none()
            if spell_check_query:
                return render_template(
                    "single_query_history.html", spell_check_query=spell_check_query
                )
            else:
                return abort(404)
        queries = SpellCheckQuery.query.filter_by(user_id=current_user.id).all()
        return render_template(
            "user_query_history.html", queries=queries, user=current_user, form=None
        )


@spell_checker.route("/login_history", methods=["GET", "POST"])
@login_required
def login_history():
    if current_user.is_admin:
        form = LoginHistoryForm()
        users = Users.query.all()
        if form.validate_on_submit():
            user = Users.query.filter_by(id=form.userid.data)
            return render_template(
                "login_history.html", form=form, users=users, user=user
            )
        return render_template("login_history.html", form=form, users=users)
    return abort(404)
