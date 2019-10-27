from flask import Flask
from flask_wtf import CSRFProtect
import binascii
import os


csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = binascii.hexlify(os.urandom(24))

    csrf.init_app(app)

    from flask_spell_check.routes import bp
    app.register_blueprint(bp)

    return app
