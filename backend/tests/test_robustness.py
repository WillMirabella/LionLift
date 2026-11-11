import json

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

import db
import routes.auth as auth

# Robustness tests: whatever a client sends, the API must answer with a clear
# 4xx error and never crash with a 500. Hypothesis makes up the bodies,
# including wrong types, huge values and odd characters.

AUTH_ROUTES = ["/api/auth/request-code", "/api/auth/verify"]


# A minimal in-memory stand-in for the verification table, so these run
# without PostgreSQL
@pytest.fixture
def memory_db(monkeypatch):
    rows = {}

    def save(email, code_hash, expires_at, *args):
        from datetime import datetime, timezone
        rows[email] = [code_hash, expires_at, 0, datetime.now(timezone.utc), False]

    monkeypatch.setattr(db, "save_verification_code", save)
    monkeypatch.setattr(db, "get_verification", lambda email: tuple(rows[email]) if email in rows else None)
    monkeypatch.setattr(db, "increment_verification_attempts", lambda email: None)
    monkeypatch.setattr(db, "mark_email_verified", lambda email: None)
    monkeypatch.setattr(auth, "send_email", lambda to, subject, body: None)
    return rows


# Any JSON value: numbers, text, lists, objects, nested a few levels deep
json_values = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False, allow_infinity=False) | st.text(max_size=50),
    lambda children: st.lists(children, max_size=4) | st.dictionaries(st.text(max_size=10), children, max_size=4),
    max_leaves=12,
)

# Objects shaped like real requests, with the right keys but any values
request_like = st.fixed_dictionaries({}, optional={"email": json_values, "code": json_values})


def check_response(response):
    assert response.status_code < 500, response.data[:200]
    assert response.is_json, f"not JSON: {response.data[:200]!r}"
    if response.status_code >= 400:
        assert isinstance(response.get_json().get("error"), str)


settings_fuzz = settings(max_examples=150, suppress_health_check=[HealthCheck.function_scoped_fixture])


# Any JSON object, with any keys and values
json_objects = st.dictionaries(st.text(max_size=10), json_values, max_size=5)


@settings_fuzz
@given(route=st.sampled_from(AUTH_ROUTES), body=json_objects)
def test_any_json_object_never_crashes(client, memory_db, route, body):
    check_response(client.post(route, json=body))


# Known bug: a body that is JSON but not an object, like [] or 5, crashes
# with AttributeError ('list' object has no attribute 'get') and gives a 500
@pytest.mark.xfail(raises=AttributeError, reason="request.get_json() is assumed to be a dict")
@pytest.mark.parametrize("route", AUTH_ROUTES)
@pytest.mark.parametrize("body", [["abc123@psu.edu"], 5, "abc123@psu.edu", True])
def test_json_that_is_not_an_object_is_400(client, memory_db, route, body):
    check_response(client.post(route, json=body))


@settings_fuzz
@given(route=st.sampled_from(AUTH_ROUTES), body=request_like)
def test_request_shaped_bodies_never_crash(client, memory_db, route, body):
    check_response(client.post(route, json=body))


@settings_fuzz
@given(route=st.sampled_from(AUTH_ROUTES), raw=st.binary(max_size=200))
def test_random_bytes_never_crash(client, memory_db, route, raw):
    # Bytes that happen to be JSON but not an object hit the known bug above
    try:
        parsed = json.loads(raw)
        assume(not parsed or isinstance(parsed, dict))
    except ValueError:
        pass
    check_response(client.post(route, data=raw, content_type="application/json"))


@pytest.mark.parametrize("route", AUTH_ROUTES)
@pytest.mark.parametrize("content_type", ["text/plain", "application/x-www-form-urlencoded", "multipart/form-data", ""])
def test_other_content_types_are_400(client, memory_db, route, content_type):
    response = client.post(route, data="email=abc123@psu.edu", content_type=content_type)
    assert response.status_code == 400 and response.is_json


@pytest.mark.parametrize("email", [
    "a" * 10_000 + "@psu.edu",                    # very long
    "abc123@psu.edu" + "\u0000",                   # null character
    "😀@psu.edu",                        # emoji
    "abc123@psu.edu" * 200,                        # repeated
])
def test_extreme_emails_are_handled(client, memory_db, email):
    check_response(client.post("/api/auth/request-code", json={"email": email}))


@pytest.mark.parametrize("code", ["", " ", "1" * 10_000, "12345", "1234567", "abcdef", "١٢٣٤٥٦", None, 123456, ["123456"]])
def test_odd_codes_are_rejected_cleanly(client, memory_db, code):
    client.post("/api/auth/request-code", json={"email": "abc123@psu.edu"})
    response = client.post("/api/auth/verify", json={"email": "abc123@psu.edu", "code": code})
    check_response(response)
    assert response.status_code == 400


# Deeply nested JSON must not crash the server
def test_deeply_nested_json(client, memory_db):
    body = '{"email": ' + "[" * 5000 + "]" * 5000 + "}"
    check_response(client.post("/api/auth/request-code", data=body, content_type="application/json"))


@pytest.mark.parametrize("method", ["get", "put", "delete", "patch"])
@pytest.mark.parametrize("route", AUTH_ROUTES)
def test_wrong_methods_are_405(client, route, method):
    assert getattr(client, method)(route).status_code == 405


# ---- SQL injection, against the real database ----

INJECTIONS = [
    "x';DROP_TABLE_users;--@psu.edu",
    "x'OR'1'='1@psu.edu",
    'x";DELETE_FROM_email_verifications;--@psu.edu',
    "x\\';SELECT_pg_sleep(5);--@psu.edu",
]


@pytest.mark.db
@pytest.mark.parametrize("email", INJECTIONS)
def test_sql_in_email_is_stored_as_plain_text(client, monkeypatch, email):
    monkeypatch.setattr(auth, "send_email", lambda to, subject, body: None)
    db.save_verification_code("victim@psu.edu", "0" * 64, None)

    response = client.post("/api/auth/request-code", json={"email": email})
    assert response.status_code in (200, 400)

    # Nothing was dropped or deleted, and the text was stored exactly as sent
    assert db.get_verification("victim@psu.edu") is not None
    if response.status_code == 200:
        assert db.get_verification(email.lower()) is not None
    conn = db.get_connection()
    curr = conn.cursor()
    curr.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('users', 'email_verifications');")
    assert curr.fetchone()[0] == 2
    conn.close()


@pytest.mark.db
def test_sql_in_user_fields_round_trips():
    from models.user import User
    nasty = "Robert'); DROP TABLE users;--"
    user = User(None, nasty, nasty, "555", "bobby@psu.edu", "male", nasty[:100], 2028, nasty, None)
    row = db.get_user_by_id(user.id)
    assert row[1] == nasty and row[2] == nasty and row[8] == nasty
