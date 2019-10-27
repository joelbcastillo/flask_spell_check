import pytest
from flask import g, session

def test_register(client, app):
    assert client.get("/register").status_code == 200

    response = client.post("/register", data={"uname": "a", "pword": "a", "2fa": "12345"})
    assert b"""<p id="success"> Success - Successfully registered.</p>""" in response.data