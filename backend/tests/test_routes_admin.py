import pytest

import bans

# Tests for routes/admin.py, the ban management API.
# The Flask test client sends requests from 127.0.0.1 with Host: localhost,
# like a request made on the server itself.

URL = "/api/admin/bans"


# ---- only requests made on the server itself, no database needed ----

@pytest.mark.parametrize("remote_addr", ["203.0.113.5", "10.0.0.2", "192.168.1.20", "2001:db8::1"])
def test_other_machines_get_404(client, remote_addr):
    environ = {"REMOTE_ADDR": remote_addr}
    assert client.get(URL, environ_base=environ).status_code == 404
    assert client.post(URL, json={"email": "a@psu.edu", "reason": "x"}, environ_base=environ).status_code == 404
    assert client.delete(URL + "/a@psu.edu", environ_base=environ).status_code == 404


@pytest.mark.parametrize("header", ["X-Forwarded-For", "X-Real-IP", "Forwarded"])
def test_forwarded_requests_get_404(client, header):
    assert client.get(URL, headers={header: "203.0.113.5"}).status_code == 404


# A website that points its own domain at 127.0.0.1 still sends its own Host
@pytest.mark.parametrize("host", ["evil.example.com", "evil.example.com:5000", "localhost.evil.com"])
def test_other_host_names_get_404(client, host):
    assert client.get(URL, headers={"Host": host}).status_code == 404


@pytest.mark.parametrize("host", ["localhost", "localhost:5000", "127.0.0.1:8000", "[::1]:5000"])
def test_local_host_names_allowed(client, monkeypatch, host):
    monkeypatch.setattr(bans, "list_bans", lambda: [])
    environ = {"REMOTE_ADDR": "::1"} if host.startswith("[") else {}
    assert client.get(URL, headers={"Host": host}, environ_base=environ).status_code == 200


# Links and plain forms can't change anything
@pytest.mark.parametrize("path", ["/api/admin/bans/a@psu.edu/delete", "/api/add_to_blacklist/a@psu.edu"])
def test_no_changes_over_get(client, monkeypatch, path):
    changes = []
    monkeypatch.setattr(bans, "ban_email", lambda *args: changes.append(args))
    monkeypatch.setattr(bans, "unban_email", lambda *args: changes.append(args))
    assert client.get(path).status_code in (400, 404, 405)
    assert changes == []


def test_form_posts_rejected(client):
    assert client.post(URL, data={"email": "a@psu.edu", "reason": "x"}).status_code == 415


# ---- endpoints against the test database ----

@pytest.mark.db
def test_create_list_get_and_remove(client):
    response = client.post(URL, json={"email": "ABC123+x@psu.edu", "reason": "harassment"})
    assert response.status_code == 201
    assert response.get_json()["email"] == "abc123@psu.edu"
    assert bans.is_banned("abc123@psu.edu")

    assert [ban["email"] for ban in client.get(URL).get_json()] == ["abc123@psu.edu"]
    assert client.get(URL + "/Abc123@psu.edu").get_json()["reason"] == "harassment"

    assert client.delete(URL + "/abc123+other@psu.edu").get_json() == {"email": "abc123@psu.edu", "removed": True}
    assert client.delete(URL + "/abc123@psu.edu").get_json()["removed"] is False
    assert client.get(URL).get_json() == []


@pytest.mark.db
def test_timed_ban(client):
    ban = client.post(URL, json={"email": "abc123@psu.edu", "reason": "no-shows", "days": 30}).get_json()
    assert ban["expires_at"] is not None


@pytest.mark.db
@pytest.mark.parametrize("body", [
    {"reason": "x"},
    {"email": "abc123@psu.edu"},
    {"email": "abc@gmail.com", "reason": "x"},
    {"email": "abc123@psu.edu", "reason": "x", "days": 0},
    {"email": "abc123@psu.edu", "reason": "x", "days": "30"},
    ["abc123@psu.edu"],
])
def test_bad_input_is_400(client, body):
    response = client.post(URL, json=body)
    assert response.status_code == 400
    assert response.get_json()["error"]


@pytest.mark.db
def test_not_banned_is_404(client):
    assert client.get(URL + "/abc123@psu.edu").status_code == 404


def test_invalid_email_in_path_is_400(client):
    assert client.get(URL + "/abc@gmail.com").status_code == 400
    assert client.delete(URL + "/abc@gmail.com").status_code == 400
