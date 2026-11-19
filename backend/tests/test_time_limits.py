import re
from datetime import datetime, timedelta, timezone

import pytest

import db
import routes.auth as auth
from services.verification import CODE_EXPIRY_MINUTES, RESEND_COOLDOWN_SECONDS

# Exact time limits for sign-in codes, checked with a clock the test controls
# instead of waiting for real time to pass.

EMAIL = "abc123@psu.edu"
START = datetime(2026, 11, 11, 17, 0, 0, tzinfo=timezone.utc)


class Clock:
    def __init__(self):
        self.now = START

    def advance(self, **delta):
        self.now += timedelta(**delta)


# Replaces datetime in routes/auth.py so datetime.now() returns the test clock
@pytest.fixture
def clock(monkeypatch):
    clock = Clock()

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return clock.now

    monkeypatch.setattr(auth, "datetime", FrozenDatetime)
    return clock


# In-memory verification table that stamps times with the test clock
@pytest.fixture
def store(monkeypatch, clock):
    rows = {}

    def save(email, code_hash, expires_at, *args):
        row = rows.setdefault(email, {"verified": False, "attempts": 0})
        row.update(code_hash=code_hash, expires_at=expires_at, attempts=0, last_sent_at=clock.now)

    def get(email):
        r = rows.get(email)
        return None if r is None else (r["code_hash"], r["expires_at"], r["attempts"], r["last_sent_at"], r["verified"])

    def increment(email):
        rows[email]["attempts"] += 1

    def verified(email):
        rows[email].update(verified=True, code_hash=None, expires_at=None)

    monkeypatch.setattr(db, "save_verification_code", save)
    monkeypatch.setattr(db, "get_verification", get)
    monkeypatch.setattr(db, "increment_verification_attempts", increment)
    monkeypatch.setattr(db, "mark_email_verified", verified)
    return rows


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(auth, "send_email", lambda to, subject, body: sent.append(body))
    return sent


def request(client):
    return client.post("/api/auth/request-code", json={"email": EMAIL})


def verify(client, outbox):
    code = re.search(r"\b(\d{6})\b", outbox[-1]).group(1)
    return client.post("/api/auth/verify", json={"email": EMAIL, "code": code})


# ---- resend cooldown ----

@pytest.mark.parametrize("seconds, allowed", [
    (0, False), (1, False), (RESEND_COOLDOWN_SECONDS - 1, False),
    (RESEND_COOLDOWN_SECONDS, True), (RESEND_COOLDOWN_SECONDS + 1, True), (3600, True),
])
def test_resend_cooldown_boundary(client, clock, store, outbox, seconds, allowed):
    request(client)
    clock.advance(seconds=seconds)
    assert (request(client).status_code == 200) is allowed
    assert len(outbox) == (2 if allowed else 1)


# Just under a second short of the cooldown still counts as too soon
def test_resend_cooldown_is_not_rounded(client, clock, store, outbox):
    request(client)
    clock.advance(seconds=RESEND_COOLDOWN_SECONDS - 0.001)
    assert request(client).status_code == 429


# ---- code expiry ----

@pytest.mark.parametrize("elapsed, works", [
    (timedelta(0), True),
    (timedelta(minutes=CODE_EXPIRY_MINUTES) - timedelta(milliseconds=1), True),
    (timedelta(minutes=CODE_EXPIRY_MINUTES), True),
    (timedelta(minutes=CODE_EXPIRY_MINUTES, milliseconds=1), False),
    (timedelta(hours=5), False),
])
def test_code_expiry_boundary(client, clock, store, outbox, elapsed, works):
    request(client)
    clock.advance(seconds=elapsed.total_seconds())
    response = verify(client, outbox)
    if works:
        assert response.get_json() == {"status": "verified"}
    else:
        assert "expired" in response.get_json()["error"]


# A new code replaces the old one: the old code stops working, the new one starts fresh
def test_new_code_replaces_old(client, clock, store, outbox):
    request(client)
    first = re.search(r"\b(\d{6})\b", outbox[-1]).group(1)
    clock.advance(minutes=9)
    request(client)
    second = re.search(r"\b(\d{6})\b", outbox[-1]).group(1)
    if first == second:
        pytest.skip("both random codes matched")
    assert client.post("/api/auth/verify", json={"email": EMAIL, "code": first}).status_code == 400
    clock.advance(minutes=9)
    assert verify(client, outbox).get_json() == {"status": "verified"}


# The expiry time saved is exactly CODE_EXPIRY_MINUTES after the code was sent
def test_saved_expiry_time(client, clock, store, outbox):
    request(client)
    assert store[EMAIL]["expires_at"] == START + timedelta(minutes=CODE_EXPIRY_MINUTES)
