from werkzeug.security import generate_password_hash, check_password_hash
from spell_checker import db, login_manager
from flask import current_app
from flask_login import UserMixin
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime as dt


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    two_factor = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    is_admin = db.Column(db.Boolean(), default=False)

    @property
    def password(self):
        raise AttributeError('Cannot read password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_two_factor(self, two_factor):
        return self.two_factor == two_factor

    def __repr__(self):
        return "<User({username!r})>".format(username=self.username)


class AuthHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_timestamp = db.Column(db.DateTime, default=dt.utcnow)
    logout_timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, login_timestamp=None, logout_timestamp=None, user_id=None):
        if not user_id or not Users.query.filter_by(id=user_id).one_or_none():
            return
        self.login_timestamp = login_timestamp
        self.logout_timestamp = logout_timestamp
        self.user_id = user_id


class SpellCheckQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text)
    result = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=dt.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, text=None, result=None, user_id=None):
        self.text = text
        self.result = result
        self.timestamp = dt.now()
        self.user_id = user_id
