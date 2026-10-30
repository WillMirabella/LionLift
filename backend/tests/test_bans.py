import re
import threading

import pytest

import bans
import db
import routes.auth as auth
from models.user import User

# Tests for bans.py against a real PostgreSQL test database.
# Each class of evasion from the design has its own test.

pytestmark = pytest.mark.db

DEVICE = "6f9619ff-8b86-d011-b42d-00c04fc964ff"
OTHER_DEVICE = "0b7a6c2e-1d3f-4a5b-9c8d-7e6f5a4b3c2d"


def new_user(email, phone="2155550100", payment=None):
    user = User(None, "Test", "User", phone, email, "female", "hi", 2028, "Biology", None)
    if payment:
        user.preferred_payment = payment
        db.update_user(user)
    return user


def decision(**identifiers):
    return bans.check_identity(list(identifiers.items()), record=False)[0]


def run_sql(query, params=()):
    conn = db.get_connection()
    curr = conn.cursor()
    curr.execute(query, params)
    rows = curr.fetchall() if curr.description else None
    conn.commit()
    conn.close()
    return rows


def events(ban_id):
    return [row[0] for row in run_sql("SELECT action FROM ban_events WHERE ban_id = %s ORDER BY id;", (ban_id,))]


# ---- strong identifiers block every written form ----

@pytest.mark.parametrize("attempt", [
    "abc123@psu.edu", "ABC123@PSU.edu", " abc123@psu.edu ", "abc123+new@psu.edu", "ａbc123@psu.edu",
])
def test_email_ban_covers_aliases(attempt):
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu")])
    assert decision(email=attempt) == bans.BLOCK


@pytest.mark.parametrize("attempt", ["215-555-0100", "(215) 555 0100", "+1 215 555 0100", "12155550100"])
def test_phone_ban_covers_formats(attempt):
    bans.create_ban("harassment", "ian", identifiers=[("phone", "2155550100")])
    assert decision(phone=attempt) == bans.BLOCK


def test_unrelated_person_allowed():
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu"), ("phone", "2155550100")])
    assert decision(email="xyz9@psu.edu", phone="2675550199") == bans.ALLOW


# ---- banning a user covers everything on file ----

def test_ban_by_user_covers_their_identifiers():
    user = new_user("abc123@psu.edu", "215-555-0100", "Cash")
    ban_id = bans.create_ban("no-shows", "ian", user_id=user.id)
    kinds = {i["kind"] for i in bans.get_ban(ban_id)["identifiers"]}
    assert kinds == {"email", "phone"}
    assert decision(phone="2155550100") == bans.BLOCK
    assert bans.is_user_banned(user.id)


# A payment method like "Cash" is shared by many people, so it must not link them
def test_payment_method_is_not_an_identifier():
    banned = new_user("abc123@psu.edu", "2155550100", "Cash")
    bans.create_ban("no-shows", "ian", user_id=banned.id)
    other = new_user("fresh1@psu.edu", "2675550199", "Cash")
    assert bans.is_user_banned(other.id) is False
    assert decision(email="fresh1@psu.edu", payment="Cash") == bans.ALLOW
    other.make_driver("2 School Ln", "Cash", None)


def test_banned_person_cannot_sign_up_again():
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu")])
    with pytest.raises(bans.BannedError):
        new_user("ABC123+second@psu.edu", "2675550199")
    assert run_sql("SELECT COUNT(*) FROM users;")[0][0] == 0


def test_banned_phone_blocks_new_account_with_new_email():
    bans.create_ban("harassment", "ian", identifiers=[("phone", "2155550100")])
    with pytest.raises(bans.BannedError):
        new_user("fresh1@psu.edu", "215.555.0100")


def test_cannot_switch_to_banned_email_later():
    bans.create_ban("harassment", "ian", identifiers=[("email", "banned1@psu.edu")])
    user = new_user("clean1@psu.edu", "2675550199")
    user.email = "Banned1@psu.edu"
    with pytest.raises(bans.BannedError):
        user.make_driver("1 School Ln", "Cash", None)
    assert db.get_user_by_id(user.id)[4] == "clean1@psu.edu"


def test_is_user_banned_through_shared_identifier():
    user = new_user("clean1@psu.edu", "2155550100")
    bans.create_ban("harassment", "ian", identifiers=[("phone", "+12155550100")])
    assert bans.is_user_banned(user.id)


# ---- weak identifiers only flag ----

def test_device_match_flags_but_allows():
    ban_id = bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu"), ("device", DEVICE)])
    result, matches = bans.check_identity([("email", "new1@psu.edu"), ("device", DEVICE.upper())], context="signup")
    assert result == bans.REVIEW and matches == [("device", ban_id)]
    assert events(ban_id)[-1] == "evasion_flagged"


def test_shared_ip_alone_never_blocks_or_flags():
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu"), ("ip", "203.0.113.7")])
    assert decision(email="other1@psu.edu", ip="203.0.113.99") == bans.ALLOW


def test_payment_and_ip_together_flag():
    bans.create_ban("harassment", "ian", identifiers=[("payment", "jane-doe"), ("ip", "203.0.113.7")])
    assert decision(payment="@Jane-Doe", ip="203.0.113.50") == bans.REVIEW


def test_strong_match_wins_over_weak():
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu")])
    assert decision(email="abc123@psu.edu", device=OTHER_DEVICE) == bans.BLOCK


# ---- lifecycle ----

def test_revoked_ban_stops_blocking():
    ban_id = bans.create_ban("mistake", "ian", identifiers=[("email", "abc123@psu.edu")])
    assert bans.revoke_ban(ban_id, "will") is True
    assert bans.revoke_ban(ban_id, "will") is False
    assert decision(email="abc123@psu.edu") == bans.ALLOW
    ban = bans.get_ban(ban_id)
    assert ban["active"] is False and ban["revoked_by"] == "will"


def test_expired_ban_stops_blocking():
    ban_id = bans.create_ban("cooldown", "ian", identifiers=[("email", "abc123@psu.edu")], duration_days=7)
    assert decision(email="abc123@psu.edu") == bans.BLOCK
    run_sql("UPDATE bans SET expires_at = NOW() - INTERVAL '1 second' WHERE id = %s;", (ban_id,))
    assert decision(email="abc123@psu.edu") == bans.ALLOW


def test_new_ban_after_revoke_works():
    user = new_user("abc123@psu.edu")
    first = bans.create_ban("first", "ian", user_id=user.id)
    bans.revoke_ban(first, "ian")
    second = bans.create_ban("second", "ian", user_id=user.id)
    assert second != first and bans.is_user_banned(user.id)


def test_list_bans():
    active = bans.create_ban("a", "ian", identifiers=[("email", "a1@psu.edu")])
    revoked = bans.create_ban("b", "ian", identifiers=[("email", "b1@psu.edu")])
    bans.revoke_ban(revoked, "ian")
    assert [b["id"] for b in bans.list_bans()] == [active]
    assert [b["id"] for b in bans.list_bans(include_inactive=True)] == [revoked, active]


# ---- storage never holds raw identifiers ----

def test_only_hashes_and_masked_hints_stored():
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu"), ("phone", "2155550100")])
    stored = run_sql("SELECT value, hint FROM ban_identifiers;")
    flat = " ".join(value + " " + hint for value, hint in stored)
    assert "abc123" not in flat and "2155550100" not in flat
    assert all(re.fullmatch(r"[0-9a-f]{64}", value) for value, _ in stored)


# ---- audit log ----

def test_audit_trail():
    ban_id = bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu")])
    bans.check_identity([("email", "abc123@psu.edu")], context="signup")
    bans.revoke_ban(ban_id, "will")
    ban = bans.get_ban(ban_id)
    assert [e["action"] for e in ban["events"]] == ["created", "blocked_attempt", "revoked"]
    assert ban["events"][0]["actor"] == "ian" and ban["events"][2]["actor"] == "will"
    assert ban["events"][1]["detail"] == {"matched": ["email"], "context": "signup"}


def test_read_only_checks_are_not_logged():
    ban_id = bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu")])
    bans.check_identity([("email", "abc123@psu.edu")], record=False)
    assert events(ban_id) == ["created"]


# ---- validation ----

@pytest.mark.parametrize("kwargs", [
    {"reason": "", "created_by": "ian", "identifiers": [("email", "a@psu.edu")]},
    {"reason": "x", "created_by": " ", "identifiers": [("email", "a@psu.edu")]},
    {"reason": "x", "created_by": "ian"},
    {"reason": "x", "created_by": "ian", "identifiers": [("email", "a@gmail.com")]},
    {"reason": "x", "created_by": "ian", "identifiers": [("email", "a@psu.edu")], "duration_days": 0},
    {"reason": "x", "created_by": "ian", "identifiers": [("email", "a@psu.edu")], "duration_days": True},
    {"reason": "x", "created_by": "ian", "user_id": 999},
])
def test_create_ban_rejects(kwargs):
    with pytest.raises(ValueError):
        bans.create_ban(**kwargs)
    assert run_sql("SELECT COUNT(*) FROM bans;")[0][0] == 0


# ---- races ----

def test_parallel_bans_of_one_user_make_one_ban():
    user = new_user("abc123@psu.edu")
    results, barrier = [], threading.Barrier(12)

    def ban():
        barrier.wait()
        results.append(bans.create_ban("spam", "ian", user_id=user.id))

    threads = [threading.Thread(target=ban) for _ in range(12)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(set(results)) == 1
    assert run_sql("SELECT COUNT(*) FROM bans;")[0][0] == 1


def test_parallel_signups_with_banned_email_all_fail():
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu")])
    outcomes, barrier = [], threading.Barrier(12)

    def signup(n):
        barrier.wait()
        try:
            new_user(f"abc123+{n}@psu.edu", "2675550199")
            outcomes.append("created")
        except bans.BannedError:
            outcomes.append("blocked")

    threads = [threading.Thread(target=signup, args=(n,)) for n in range(12)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert outcomes.count("blocked") == 12
    assert run_sql("SELECT COUNT(*) FROM users;")[0][0] == 0


# ---- migration from the old blacklist table ----

def test_migrate_legacy_blacklist():
    run_sql("CREATE TABLE blacklist (id SERIAL PRIMARY KEY, email VARCHAR(100));")
    run_sql("INSERT INTO blacklist (email) VALUES ('ABC@psu.edu'), ('abc@psu.edu'), ('junk'), ('x@gmail.com');")
    assert bans.migrate_legacy_blacklist() == 1
    assert bans.migrate_legacy_blacklist() == 0
    assert decision(email="abc+1@psu.edu") == bans.BLOCK


def test_migrate_without_legacy_table():
    assert bans.migrate_legacy_blacklist() == 0


# ---- email verification honors bans ----

@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(auth, "send_email", lambda to, subject, body: sent.append(body))
    return sent


def test_banned_alias_gets_no_code(client, outbox):
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu")])
    response = client.post("/api/auth/request-code", json={"email": "ABC123@psu.edu"})
    assert response.get_json() == {"status": "code_sent"}
    assert outbox == []


def test_banned_device_blocks_code_only_with_strong_match(client, outbox):
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu"), ("device", DEVICE)])
    client.post("/api/auth/request-code", json={"email": "fresh1@psu.edu"}, headers={"X-Device-Id": DEVICE})
    assert len(outbox) == 1


def test_ban_after_code_blocks_verify(client, outbox):
    client.post("/api/auth/request-code", json={"email": "abc123@psu.edu"})
    code = re.search(r"\b(\d{6})\b", outbox[-1]).group(1)
    bans.create_ban("harassment", "ian", identifiers=[("email", "abc123@psu.edu")])
    response = client.post("/api/auth/verify", json={"email": "abc123@psu.edu", "code": code})
    assert response.status_code == 403
    assert not db.is_email_verified("abc123@psu.edu")
