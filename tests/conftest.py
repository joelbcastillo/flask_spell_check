import os
import tempfile

import pytest

from flask_spell_check import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)