from flask import Blueprint

bp = Blueprint("main", __name__)

from flask_spell_check.main import routes
