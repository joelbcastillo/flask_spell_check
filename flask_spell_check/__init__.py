from flask import Flask
from flask_wtf.csrf import CsrfProtect
from flask_login import LoginManager

from config import Config

import os

csrf = CsrfProtect()
login_manager = LoginManager()
login_manager.login_view = "main.login"


def create_app(config_class=Config):
    """Initialize the core application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    csrf.init_app(app)
    login_manager.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flask_spell_check.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app
