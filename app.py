import os

from spell_checker import create_app

app = create_app(os.getenv("FLASK_CONFIG") or "default")
