import json
import re
import threading
import urllib.error
import urllib.request

import pytest
from werkzeug.serving import make_server

import db
import routes.auth as auth

# System tests: the whole backend runs as a real HTTP server on a free port,
# backed by the PostgreSQL test database, and is used the way the app would use
# it, over the network. These catch problems the in-process tests can't, like
# JSON encoding, status codes and running several requests at once.

pytestmark = [pytest.mark.db, pytest.mark.system]


# Starts the real app on 127.0.0.1 with a free port, and stops it after the test
@pytest.fixture
def server():
    from app import app
    httpd = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    thread.join(timeout=5)


# Collects sent emails instead of printing them
@pytest.fixture
def outbox(monkeypatch):
    sent = []
    lock = threading.Lock()

    def capture(to, subject, body):
        with lock:
            sent.append((to, body))

    monkeypatch.setattr(auth, "send_email", capture)
    return sent


# Sends one HTTP request and returns (status code, parsed JSON or text)
def call(base, method, path, body=None, raw=None, content_type="application/json"):
    data = raw if raw is not None else (None if body is None else json.dumps(body).encode())
    request = urllib.request.Request(base + path, data=data, method=method)
    if data is not None:
        request.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status, text = response.status, response.read().decode()
    # 4xx and 5xx responses come back as errors, but still have a body
    except urllib.error.HTTPError as error:
        status, text = error.code, error.read().decode()
    try:
        return status, json.loads(text)
    except ValueError:
        return status, text


def code_for(outbox, email):
    body = [body for to, body in outbox if to == email][-1]
    return re.search(r"\b(\d{6})\b", body).group(1)


def wrong_code(code):
    return "000000" if code != "000000" else "111111"


# ---- basics ----

def test_home_page(server):
    status, body = call(server, "GET", "/")
    assert status == 200 and "Hello" in body


def test_unknown_route_is_404(server):
    assert call(server, "GET", "/api/nothing-here")[0] == 404


# ---- signing in ----

def test_sign_in_journey(server, outbox):
    email = "abc123@psu.edu"
    assert call(server, "POST", "/api/auth/request-code", {"email": "ABC123@PSU.EDU"}) == (200, {"status": "code_sent"})

    # Asking again right away is refused
    status, body = call(server, "POST", "/api/auth/request-code", {"email": email})
    assert status == 429 and body["error"]

    # A wrong code doesn't sign in, the right one does
    code = code_for(outbox, email)
    assert call(server, "POST", "/api/auth/verify", {"email": email, "code": wrong_code(code)})[1] == {"error": "Incorrect code"}
    assert call(server, "POST", "/api/auth/verify", {"email": email, "code": f" {code} "}) == (200, {"status": "verified"})
    assert db.is_email_verified(email)

    # Once verified, no new code is sent
    assert call(server, "POST", "/api/auth/request-code", {"email": email}) == (200, {"status": "already_verified"})
    assert len(outbox) == 1


def test_lockout_after_five_wrong_codes(server, outbox):
    email = "abc123@psu.edu"
    call(server, "POST", "/api/auth/request-code", {"email": email})
    code = code_for(outbox, email)
    for _ in range(5):
        call(server, "POST", "/api/auth/verify", {"email": email, "code": wrong_code(code)})
    status, body = call(server, "POST", "/api/auth/verify", {"email": email, "code": code})
    assert status == 400 and "Too many attempts" in body["error"]
    assert not db.is_email_verified(email)


@pytest.mark.parametrize("raw, content_type", [
    (b"", "application/json"),
    (b"not json", "application/json"),
    (b"email=abc123@psu.edu", "application/x-www-form-urlencoded"),
    (b'{"email": 5}', "application/json"),
    (b'{"email": "abc@gmail.com"}', "application/json"),
])
def test_bad_sign_in_requests_are_400(server, outbox, raw, content_type):
    status, body = call(server, "POST", "/api/auth/request-code", raw=raw, content_type=content_type)
    assert status == 400 and body["error"]
    assert outbox == []


def test_many_sign_ins_at_once(server, outbox):
    emails = [f"user{i}@psu.edu" for i in range(12)]
    results = {}

    def sign_in(email):
        results[email] = call(server, "POST", "/api/auth/request-code", {"email": email})[0]

    threads = [threading.Thread(target=sign_in, args=(email,)) for email in emails]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert all(results[email] == 200 for email in emails)
    assert sorted(to for to, body in outbox) == sorted(emails)
    assert all(db.get_verification(email) is not None for email in emails)


# ---- browsing (needs the #22/#23 users route) ----

def test_new_users_show_up_in_browse_without_private_fields(server, outbox):
    pytest.importorskip("routes.users")
    from models.user import User

    # Sign in, then save a profile the way the sign-up screen will
    for email, last in (("aa1@psu.edu", "Zimmer"), ("bb2@psu.edu", "Adams")):
        call(server, "POST", "/api/auth/request-code", {"email": email})
        call(server, "POST", "/api/auth/verify", {"email": email, "code": code_for(outbox, email)})
        User(None, "Test", last, "2155550100", email, "female", "hi", 2028, "Biology", [(9, 17)] * 5)

    status, users = call(server, "GET", "/api/users/?sort=last_name")
    assert status == 200
    assert [user["last_name"] for user in users] == ["Adams", "Zimmer"]
    for user in users:
        assert not {"phone", "email", "address"} & set(user)
