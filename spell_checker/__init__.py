from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import CsrfProtect
from flask_script import Manager
from config import Config, config

db = SQLAlchemy()
csrf = CsrfProtect()
login_manager = LoginManager()
bcrypt = Bcrypt()
manager = Manager()
migrate = Migrate()


def create_app(config_name="default"):
    """
    Set up the Flask Application context.
    :param config_name: Configuration for specific application context.
    :return: Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    manager.add_command("db", MigrateCommand)

    with app.app_context():
        login_manager.login_view = "spell_checker.login"

    @app.after_request
    def add_security_headers(response):
        response.headers[
            "Content-Security-Policy"
        ] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if session.get("username") is not None:
            response.set_cookie(
                "username",
                session.get("username"),
                secure=False,
                httponly=True,
                samesite="Lax",
            )

        return response

    from .views import spell_checker
    from . import models, views

    app.register_blueprint(spell_checker)
