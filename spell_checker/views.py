from spell_checker import db
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    current_app,
    Blueprint,
)
from flask_login import current_user, login_user, logout_user, login_required

from spell_checker.forms import RegisterForm, LoginForm, SpellCheckForm
from spell_checker.models import Users

spell_checker = Blueprint("spell_checker", __name__, template_folder="templates")


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

        flash("success")
        
        return redirect(url_for("spell_checker.login"))
    
    return render_template("register.html", form=form)

@spell_checker.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('spell_checker.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).one_or_none()
        
        if not (user or user.check_password(form.password.data)):
            flash("Incorrect username or password", "result")
            return redirect(url_for('spell_check.login'))

        if user.two_factor is not None and not user.check_two_factor(form.two_factor.data):
            flash('Failure: Two-factor authentication', 'result')
            return redirect(url_for("spell_check.login"))

        login_user(user)

        flash("success", 'result')


