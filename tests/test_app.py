import pytest
from flask import g, session

def test_register(client, app):
    assert client.get("/register").status_code == 200

    response = client.post("/register", data={"uname": "a", "pword": "a", "2fa": "12345"})
    assert b"""<p id="success"> Success - Successfully registered.</p>""" in response.data

    response = client.post("/register", data={"uname": "b", "pword": "a", "2fa": "12345"})
    assert b"""<p id="success"> Success - Successfully registered.</p>""" in response.data

    response = client.post("/register", data={"uname": "c", "pword": "a"})
    assert b"""<p id="success"> Success - Successfully registered.</p>""" in response.data

    response = client.post("/register", data={"uname": "a", "pword": "a", "2fa": "12345"})
    assert b"""<p id="success"> Failure - Unable to register. Please try again.</p>""" in response.data

    response = client.post("/register", data={"pword": "a", "2fa": "12345"})
    assert b"""<p id="success"> Failure - Unable to register. Please try again.</p>""" in response.data

    response = client.post("/register", data={"uname": "a", "2fa": "12345"})
    assert b"""<p id="success"> Failure - Unable to register. Password cannot be null.</p>""" in response.data


def test_login(client, app):
    assert client.get('/login').status_code == 200

    response = client.post("/login", data={"uname": "a", "pword": "a", "2fa": "12345"})
    assert b"""<p id="result"> Success</p>""" in response.data
    
    response = client.post("/login", data={"uname": "c", "pword": "a"})
    assert b"""<p id="result"> Two-factor failure</p>""" in response.data

    response = client.post("/login", data={"uname": "a", "pword": "b", "2fa": "12345"})
    assert b"""<p id="result"> Incorrect</p>""" in response.data

    response = client.post("/login", data={"pword": "a", "2fa": "12345"})
    assert b"""<p id="result"> Incorrect</p>""" in response.data

    response = client.post("/login", data={"uname": "a", "2fa": "12345"})
    assert b"""<p id="result"> Incorrect</p>""" in response.data

def test_login_required(client, app):
    response = client.get('/spell_check')

    assert 302 == response.status_code
    assert "http://localhost/login" == response.headers['Location']