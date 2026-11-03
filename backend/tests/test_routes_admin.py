import pytest

import bans
from models.user import User

# Tests for routes/admin.py, the ban management API

IAN = "ian-token-0123456789abcdef"
WILL = "will-token-0123456789abcdef"


@pytest.fixture(autouse=True)
def tokens(monkeypatch):
    monkeypatch.setenv("LIONLIFT_ADMIN_TOKENS", f"ian:{IAN}, will:{WILL}")


def auth(token=IAN):
    return {"Authorization": f"Bearer {token}"}


# ---- access control, no database needed ----

def test_admin_api_off_without_tokens(client, monkeypatch):
    monkeypatch.delenv("LIONLIFT_ADMIN_TOKENS")
    assert client.get("/api/admin/bans", headers=auth()).status_code == 503


@pytest.mark.parametrize("headers", [
    {}, {"Authorization": "Bearer wrong-token-0123456789"}, {"Authorization": IAN},
    {"Authorization": "Basic " + IAN}, {"Authorization": "Bearer "},
])
def test_requests_without_valid_token_rejected(client, headers):
    assert client.get("/api/admin/bans", headers=headers).status_code == 401
    assert client.post("/api/admin/bans", json={"reason": "x"}, headers=headers).status_code == 401
    assert client.delete("/api/admin/bans/1", headers=headers).status_code == 401


def test_short_tokens_are_ignored(client, monkeypatch):
    monkeypatch.setenv("LIONLIFT_ADMIN_TOKENS", "ian:short")
    assert client.get("/api/admin/bans", headers={"Authorization": "Bearer short"}).status_code == 503


# A link or form on another site can only send GET or a form POST without the header
@pytest.mark.parametrize("method, path", [
    ("get", "/api/admin/bans/1/delete"), ("get", "/api/add_to_blacklist/x@psu.edu"),
])
def test_no_state_changes_over_get(client, method, path):
    assert getattr(client, method)(path).status_code in (404, 405)


def test_form_posts_rejected(client):
    response = client.post("/api/admin/bans", data={"reason": "x"}, headers=auth())
    assert response.status_code == 415


# ---- endpoints against the test database ----

@pytest.mark.db
def test_create_ban_by_identifiers(client):
    response = client.post("/api/admin/bans", headers=auth(), json={
        "reason": "harassment", "identifiers": {"email": "ABC123+x@psu.edu", "phone": "215-555-0100"},
    })
    assert response.status_code == 201
    ban = response.get_json()
    assert ban["created_by"] == "ian" and ban["active"] and ban["expires_at"] is None
    assert {i["hint"] for i in ban["identifiers"]} == {"ab***@psu.edu", "***0100"}
    assert bans.check_identity([("email", "abc123@psu.edu")], record=False)[0] == bans.BLOCK


@pytest.mark.db
def test_create_ban_by_user_with_duration(client):
    user = User(None, "Test", "User", "2155550100", "abc123@psu.edu", "f", "hi", 2028, "Bio", None)
    response = client.post("/api/admin/bans", headers=auth(WILL),
                           json={"reason": "no-shows", "user_id": user.id, "duration_days": 30})
    ban = response.get_json()
    assert response.status_code == 201
    assert ban["user_id"] == user.id and ban["created_by"] == "will" and ban["expires_at"]


@pytest.mark.db
@pytest.mark.parametrize("body", [
    {"identifiers": {"email": "a@psu.edu"}},
    {"reason": "x"},
    {"reason": "x", "identifiers": {"email": "a@gmail.com"}},
    {"reason": "x", "identifiers": {"plate": "ABC123"}},
    {"reason": "x", "identifiers": ["a@psu.edu"]},
    {"reason": "x", "user_id": "5"},
    {"reason": "x", "user_id": 999},
    {"reason": "x", "identifiers": {"email": "a@psu.edu"}, "duration_days": -1},
])
def test_create_ban_bad_input(client, body):
    response = client.post("/api/admin/bans", headers=auth(), json=body)
    assert response.status_code == 400
    assert response.get_json()["error"]


@pytest.mark.db
def test_list_get_and_revoke(client):
    created = client.post("/api/admin/bans", headers=auth(),
                          json={"reason": "spam", "identifiers": {"email": "abc123@psu.edu"}}).get_json()
    ban_id = created["id"]

    assert [b["id"] for b in client.get("/api/admin/bans", headers=auth()).get_json()] == [ban_id]

    detail = client.get(f"/api/admin/bans/{ban_id}", headers=auth()).get_json()
    assert detail["events"][0]["action"] == "created"

    response = client.delete(f"/api/admin/bans/{ban_id}", headers=auth(WILL))
    assert response.get_json() == {"id": ban_id, "revoked": True}
    assert client.delete(f"/api/admin/bans/{ban_id}", headers=auth()).get_json()["revoked"] is False

    assert client.get("/api/admin/bans", headers=auth()).get_json() == []
    everything = client.get("/api/admin/bans?all=1", headers=auth()).get_json()
    assert everything[0]["revoked_by"] == "will"


@pytest.mark.db
def test_missing_ban_is_404(client):
    assert client.get("/api/admin/bans/999", headers=auth()).status_code == 404
    assert client.delete("/api/admin/bans/999", headers=auth()).status_code == 404


@pytest.mark.db
def test_check_endpoint(client):
    client.post("/api/admin/bans", headers=auth(), json={"reason": "spam", "identifiers": {"email": "abc123@psu.edu"}})
    result = client.post("/api/admin/check", headers=auth(), json={"identifiers": {"email": "ABC123@psu.edu"}}).get_json()
    assert result["decision"] == bans.BLOCK
    result = client.post("/api/admin/check", headers=auth(), json={"identifiers": {"email": "new1@psu.edu"}}).get_json()
    assert result == {"decision": bans.ALLOW, "matches": []}
    bad = client.post("/api/admin/check", headers=auth(), json={"identifiers": {"email": "a@gmail.com"}})
    assert bad.status_code == 400
