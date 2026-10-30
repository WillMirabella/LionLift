import re
from datetime import datetime, timedelta, timezone

import pytest

import bans
import db
import routes.auth as auth

# Tests for routes/auth.py, the email verification endpoints.
# The database functions are replaced with an in-memory store that behaves the
# same way as the SQL in db.py, so these run without PostgreSQL.
# test_db.py covers the same flow against the real database.

REQUEST = "/api/auth/request-code"
VERIFY = "/api/auth/verify"
EMAIL = "abc123@psu.edu"


class FakeStore:
    def __init__(self):
        self.rows = {}

    # Same as save_verification_code: replaces the code and resets attempts
    def save(self, email, code_hash, expires_at):
        row = self.rows.setdefault(email, {"verified": False})
        row.update(code_hash=code_hash, expires_at=expires_at, attempts=0,
                   last_sent_at=datetime.now(timezone.utc))

    def get(self, email):
        row = self.rows.get(email)
        if row is None:
            return None
        return (row["code_hash"], row["expires_at"], row["attempts"], row["last_sent_at"], row["verified"])

    def increment(self, email):
        if email in self.rows:
            self.rows[email]["attempts"] += 1

    def mark_verified(self, email):
        if email in self.rows:
            self.rows[email].update(verified=True, code_hash=None, expires_at=None)


@pytest.fixture
def store(monkeypatch):
    fake = FakeStore()
    monkeypatch.setattr(db, "save_verification_code", fake.save)
    monkeypatch.setattr(db, "get_verification", fake.get)
    monkeypatch.setattr(db, "increment_verification_attempts", fake.increment)
    monkeypatch.setattr(db, "mark_email_verified", fake.mark_verified)
    return fake


# Ban checks are tested in test_bans.py; here they allow everyone unless a test
# lists emails to block
@pytest.fixture(autouse=True)
def blocked(monkeypatch):
    blocked_emails = set()

    def check(identifiers, context=None, strict=False, record=True):
        emails = {value for kind, value in identifiers if kind == "email"}
        return (bans.BLOCK, [("email", 1)]) if emails & blocked_emails else (bans.ALLOW, [])

    monkeypatch.setattr(bans, "check_identity", check)
    return blocked_emails


# Collects sent emails instead of printing them
@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(auth, "send_email", lambda to, subject, body: sent.append((to, subject, body)))
    return sent


def code_from(outbox):
    return re.search(r"\b(\d{6})\b", outbox[-1][2]).group(1)


def wrong_code(code):
    return "000000" if code != "000000" else "111111"


# Moves a stored timestamp into the past to simulate time passing
def age(store, field, **delta):
    store.rows[EMAIL][field] -= timedelta(**delta)


# ---- request-code ----

@pytest.mark.parametrize("body", [None, {}, {"email": None}, {"email": 123}, {"mail": EMAIL}])
def test_request_requires_email(client, store, outbox, body):
    response = client.post(REQUEST, json=body) if body is not None else client.post(REQUEST, data="not json")
    assert response.status_code == 400
    assert outbox == []


@pytest.mark.parametrize("email", ["abc@gmail.com", "abc@psu.edu.evil.com", "abc", "a b@psu.edu"])
def test_request_rejects_non_psu(client, store, outbox, email):
    response = client.post(REQUEST, json={"email": email})
    assert response.status_code == 400
    assert outbox == []


def test_request_sends_code(client, store, outbox):
    response = client.post(REQUEST, json={"email": EMAIL})
    assert response.status_code == 200
    assert response.get_json() == {"status": "code_sent"}
    to, subject, body = outbox[0]
    assert to == EMAIL and "verification code" in subject.lower()
    assert re.search(r"\b\d{6}\b", body)


def test_request_normalizes_email(client, store, outbox):
    client.post(REQUEST, json={"email": "  ABC123@PSU.edu "})
    assert outbox[0][0] == EMAIL
    assert EMAIL in store.rows


def test_code_is_stored_hashed(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    code = code_from(outbox)
    assert store.rows[EMAIL]["code_hash"] != code
    assert len(store.rows[EMAIL]["code_hash"]) == 64


def test_resend_cooldown(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    response = client.post(REQUEST, json={"email": EMAIL})
    assert response.status_code == 429
    assert len(outbox) == 1


def test_resend_after_cooldown_replaces_code(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    first = code_from(outbox)
    age(store, "last_sent_at", seconds=61)
    assert client.post(REQUEST, json={"email": EMAIL}).status_code == 200
    second = code_from(outbox)
    if first != second:
        assert client.post(VERIFY, json={"email": EMAIL, "code": first}).status_code == 400
    assert client.post(VERIFY, json={"email": EMAIL, "code": second}).status_code == 200


def test_request_after_verified(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    client.post(VERIFY, json={"email": EMAIL, "code": code_from(outbox)})
    response = client.post(REQUEST, json={"email": EMAIL})
    assert response.get_json() == {"status": "already_verified"}
    assert len(outbox) == 1


# ---- verify ----

@pytest.mark.parametrize("body", [{}, {"email": EMAIL}, {"code": "123456"}, {"email": EMAIL, "code": 123456}])
def test_verify_requires_email_and_code(client, store, body):
    assert client.post(VERIFY, json=body).status_code == 400


def test_verify_without_request(client, store):
    response = client.post(VERIFY, json={"email": EMAIL, "code": "123456"})
    assert response.status_code == 400


def test_verify_correct_code(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    response = client.post(VERIFY, json={"email": EMAIL.upper(), "code": " " + code_from(outbox) + " "})
    assert response.status_code == 200
    assert response.get_json() == {"status": "verified"}
    assert store.rows[EMAIL]["verified"] is True
    assert store.rows[EMAIL]["code_hash"] is None


def test_verify_again_after_success(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    client.post(VERIFY, json={"email": EMAIL, "code": code_from(outbox)})
    response = client.post(VERIFY, json={"email": EMAIL, "code": "999999"})
    assert response.get_json() == {"status": "verified"}


def test_wrong_code_counts_attempt(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    response = client.post(VERIFY, json={"email": EMAIL, "code": wrong_code(code_from(outbox))})
    assert response.status_code == 400
    assert store.rows[EMAIL]["attempts"] == 1


def test_lockout_after_five_wrong(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    code = code_from(outbox)
    for _ in range(5):
        client.post(VERIFY, json={"email": EMAIL, "code": wrong_code(code)})
    response = client.post(VERIFY, json={"email": EMAIL, "code": code})
    assert response.status_code == 400
    assert "Too many attempts" in response.get_json()["error"]


def test_correct_code_on_fifth_try(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    code = code_from(outbox)
    for _ in range(4):
        client.post(VERIFY, json={"email": EMAIL, "code": wrong_code(code)})
    assert client.post(VERIFY, json={"email": EMAIL, "code": code}).status_code == 200


def test_expired_code(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    age(store, "expires_at", minutes=11)
    response = client.post(VERIFY, json={"email": EMAIL, "code": code_from(outbox)})
    assert response.status_code == 400
    assert "expired" in response.get_json()["error"].lower()


def test_code_bound_to_its_email(client, store, outbox):
    client.post(REQUEST, json={"email": EMAIL})
    client.post(REQUEST, json={"email": "other@psu.edu"})
    other_code = code_from(outbox)
    mine = store.rows[EMAIL]
    if auth.check_code(other_code, mine["code_hash"]):
        pytest.skip("both random codes matched")
    assert client.post(VERIFY, json={"email": EMAIL, "code": other_code}).status_code == 400


# ---- banned emails ----

def test_banned_email_gets_normal_reply_but_no_code(client, store, outbox, blocked):
    blocked.add(EMAIL)
    response = client.post(REQUEST, json={"email": EMAIL})
    assert response.status_code == 200
    assert response.get_json() == {"status": "code_sent"}
    assert outbox == []
    assert EMAIL not in store.rows


def test_banned_email_cannot_verify(client, store, outbox, blocked):
    client.post(REQUEST, json={"email": EMAIL})
    blocked.add(EMAIL)
    response = client.post(VERIFY, json={"email": EMAIL, "code": code_from(outbox)})
    assert response.status_code == 403
    assert store.rows[EMAIL]["verified"] is False
