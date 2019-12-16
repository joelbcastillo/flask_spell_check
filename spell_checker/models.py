from werkzeug.security import generate_password_hash, check_password_hash
from spell_checker import bcrypt, db, login_manager
from flask import current_app
from flask_login import UserMixin
from datetime import datetime as dt


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(128), nullable=False)
    two_factor = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    is_admin = db.Column(db.Boolean(), default=False)

    def __init__(self, username, password=None, two_factor=None, is_admin=False):
        self.username = username
        self.password = self.set_password(password)
        self.two_factor = two_factor
        self.is_admin = is_admin

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def check_two_factor(self, two_factor):
        return self.two_factor == two_factor

    def __repr__(self):
        return "<User({username!r})>".format(username=self.username)

class AuthHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_timestamp = db.Column(db.DateTime, default=dt.utcnow)
    logout_timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

