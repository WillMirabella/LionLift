import pytest
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_jwt_extended import decode_token

import db

# Tests for creating an account (POST /api/auth/set-password) and signing in
# (POST /api/auth/login). Users are kept in memory here; the end of the file
# runs the same steps against the real database.

SET = "/api/auth/set-password"
LOGIN = "/api/auth/login"
EMAIL = "abc123@psu.edu"
GOOD = "abc12345!"


# In-memory users table: email -> saved User
@pytest.fixture
def users(monkeypatch):
    saved = {}

    def get_by_email(email):
        user = saved.get(email)
        return None if user is None else (1, user.email, user.password)

    monkeypatch.setattr(db, "get_user_by_email", get_by_email)
    monkeypatch.setattr(db, "insert_user", lambda user: saved.setdefault(user.email, user) and 1)
    return saved


def sign_up(client, email=EMAIL, password=GOOD):
    return client.post(SET, json={"email": email, "password": password})


# ---- creating an account ----

def test_sign_up_saves_a_hashed_password(client, users):
    response = sign_up(client)
    assert response.status_code == 201
    stored = users[EMAIL].password
    assert stored != GOOD and stored.startswith("$2")
    assert check_password_hash(stored, GOOD)


def test_same_email_twice_is_refused(client, users):
    sign_up(client)
    response = sign_up(client, password="other123!")
    assert response.status_code == 400 and "exists" in response.get_json()["error"]


@pytest.mark.parametrize("body", [{}, {"email": EMAIL}, {"password": GOOD}, {"email": "", "password": GOOD}])
def test_missing_fields(client, users, body):
    response = client.post(SET, json=body)
    assert response.status_code == 400 and response.get_json()["error"]


# Rules: at least 8 characters, with letters, numbers and a special character
@pytest.mark.parametrize("password", ["abc12!", "abcdefg!", "1234567!", "abcdefgh1", "        "])
def test_weak_passwords_are_refused(client, users, password):
    assert sign_up(client, password=password).status_code == 400
    assert EMAIL not in users


@pytest.mark.parametrize("password", ["abc12345!", "Password1$", "x" * 50 + "9#", "pässwört1!"])
def test_strong_passwords_are_accepted(client, users, password):
    assert sign_up(client, password=password).status_code == 201


# ---- signing in ----

def test_login_gives_a_token_for_this_email(client, users):
    sign_up(client)
    response = client.post(LOGIN, json={"email": EMAIL, "password": GOOD})
    assert response.status_code == 200
    with client.application.app_context():
        claims = decode_token(response.get_json()["token"])
    assert claims["sub"] == EMAIL
    assert claims["exp"] > claims["iat"]


# Wrong password and unknown email look the same, so the login form can't be
# used to find out who has an account
def test_failed_logins_look_the_same(client, users):
    sign_up(client)
    wrong_password = client.post(LOGIN, json={"email": EMAIL, "password": "nope12345!"})
    unknown_email = client.post(LOGIN, json={"email": "nobody@psu.edu", "password": GOOD})
    assert wrong_password.status_code == unknown_email.status_code == 400
    assert wrong_password.get_json() == unknown_email.get_json()


@pytest.mark.parametrize("body", [{}, {"email": EMAIL}, {"password": GOOD}])
def test_login_missing_fields(client, users, body):
    assert client.post(LOGIN, json=body).status_code == 400


def test_token_from_another_secret_is_rejected(client, users):
    from flask import Flask
    from flask_jwt_extended import JWTManager, create_access_token
    other = Flask("other")
    other.config["JWT_SECRET_KEY"] = "a-completely-different-secret-key-123"
    JWTManager(other)
    with other.app_context():
        forged = create_access_token(identity=EMAIL)
    with client.application.app_context(), pytest.raises(Exception):
        decode_token(forged)


# ---- known bugs (recorded, not fixed here) ----

# Anyone can create an account for any email, without proving they own it
@pytest.mark.xfail(reason="set-password doesn't check the email was verified")
def test_unverified_email_cannot_sign_up(client, users, monkeypatch):
    monkeypatch.setattr(db, "is_email_verified", lambda email: False)
    assert sign_up(client).status_code in (400, 403)


@pytest.mark.xfail(reason="set-password doesn't check for a @psu.edu address")
def test_non_psu_email_cannot_sign_up(client, users):
    assert sign_up(client, email="someone@gmail.com").status_code == 400


# A password with no special character gets the wrong message
@pytest.mark.xfail(reason="the special-character rule reports 'upper and lower case'")
def test_missing_special_character_message(client, users):
    assert "special" in sign_up(client, password="abcdefgh1").get_json()["error"]


@pytest.mark.xfail(raises=TypeError, reason="a number as the password crashes len()")
def test_number_as_password_is_400(client, users):
    assert client.post(SET, json={"email": EMAIL, "password": 12345678}).status_code == 400


# Users created without a password (example.py does this) crash login
@pytest.mark.xfail(raises=(TypeError, ValueError), reason="check_password_hash gets None")
def test_login_for_user_without_password_is_400(client, monkeypatch):
    monkeypatch.setattr(db, "get_user_by_email", lambda email: (1, email, None))
    assert client.post(LOGIN, json={"email": EMAIL, "password": GOOD}).status_code == 400


# The signing key is written in app.py, so anyone with the code can make tokens
@pytest.mark.xfail(reason="JWT_SECRET_KEY is hardcoded and under 32 bytes")
def test_jwt_secret_is_not_the_placeholder(client):
    secret = client.application.config["JWT_SECRET_KEY"]
    assert secret != "secret-string-change-this-later" and len(secret) >= 32


# ---- against the real database ----

@pytest.mark.db
def test_account_flow_with_database(client):
    assert sign_up(client).status_code == 201
    row = db.get_user_by_email(EMAIL)
    assert row is not None and check_password_hash(row[2], GOOD)
    assert sign_up(client).status_code == 400
    assert client.post(LOGIN, json={"email": EMAIL, "password": GOOD}).status_code == 200
    assert client.post(LOGIN, json={"email": EMAIL, "password": "wrong123!"}).status_code == 400


@pytest.mark.db
def test_password_is_never_stored_plain(client):
    sign_up(client)
    conn = db.get_connection()
    curr = conn.cursor()
    curr.execute("SELECT COUNT(*) FROM users WHERE password = %s;", (GOOD,))
    assert curr.fetchone()[0] == 0
    conn.close()
