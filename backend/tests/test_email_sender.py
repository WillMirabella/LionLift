import smtplib

import pytest

import routes.auth as auth
import services.email_sender as email_sender
from services.email_sender import get_gmail_credentials, send_email

# Tests for services/email_sender.py. No test ever reaches Gmail: without
# settings the sender prints, and with settings the SMTP connection is fake.


# ---- without Gmail settings it prints ----

def test_send_email_prints_message(capsys):
    send_email("abc123@psu.edu", "Your code", "Your verification code is 123456.")
    printed = capsys.readouterr().out
    assert "EMAIL to abc123@psu.edu" in printed
    assert "Subject: Your code" in printed
    assert "Your verification code is 123456." in printed


def test_send_email_returns_nothing(capsys):
    assert send_email("a@psu.edu", "s", "b") is None


@pytest.mark.parametrize("address, password", [
    ("", ""), ("team@gmail.com", ""), ("", "abcdabcdabcdabcd"),
    (email_sender.PLACEHOLDER_ADDRESS, "abcdabcdabcdabcd"),
    ("team@gmail.com", email_sender.PLACEHOLDER_PASSWORD),
])
def test_missing_or_placeholder_settings_mean_no_gmail(monkeypatch, address, password):
    monkeypatch.setenv("GMAIL_ADDRESS", address)
    monkeypatch.setenv("GMAIL_APP_PASSWORD", password)
    assert get_gmail_credentials() is None


def test_app_password_spaces_are_removed(monkeypatch):
    monkeypatch.setenv("GMAIL_ADDRESS", " team@gmail.com ")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "abcd efgh ijkl mnop")
    assert get_gmail_credentials() == ("team@gmail.com", "abcdefghijklmnop")


# ---- with Gmail settings it sends through SMTP ----

class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout=None):
        self.host, self.port, self.timeout = host, port, timeout
        self.logged_in, self.sent = None, []
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def login(self, address, password):
        self.logged_in = (address, password)

    def send_message(self, message):
        self.sent.append(message)


@pytest.fixture
def gmail(monkeypatch):
    FakeSMTP.instances = []
    monkeypatch.setenv("GMAIL_ADDRESS", "team@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "abcd efgh ijkl mnop")
    monkeypatch.setattr(email_sender.smtplib, "SMTP_SSL", FakeSMTP)
    return FakeSMTP


def test_sends_through_gmail(gmail, capsys):
    send_email("abc123@psu.edu", "Your code", "Your verification code is 123456.")
    server = gmail.instances[0]
    assert (server.host, server.port) == ("smtp.gmail.com", 465)
    assert server.timeout == 10
    assert server.logged_in == ("team@gmail.com", "abcdefghijklmnop")
    message = server.sent[0]
    assert message["To"] == "abc123@psu.edu"
    assert message["From"] == "LionLift <team@gmail.com>"
    assert message["Subject"] == "Your code"
    assert "123456" in message.get_content()
    assert capsys.readouterr().out == ""


def test_gmail_errors_reach_the_caller(gmail, monkeypatch):
    def refuse(self, address, password):
        raise smtplib.SMTPAuthenticationError(535, b"bad credentials")

    monkeypatch.setattr(gmail, "login", refuse)
    with pytest.raises(smtplib.SMTPAuthenticationError):
        send_email("abc123@psu.edu", "s", "b")


# ---- what sign-in does when sending fails ----

# The code is only saved after the email goes out, so a failed send leaves no
# code behind and no cooldown, and the student can try again right away
def test_failed_send_is_502_and_saves_nothing(client, monkeypatch):
    saved = []
    monkeypatch.setattr(auth.db, "get_verification", lambda email: None)
    monkeypatch.setattr(auth.db, "save_verification_code", lambda *args: saved.append(args))

    def broken(to, subject, body):
        raise smtplib.SMTPServerDisconnected("connection lost")

    monkeypatch.setattr(auth, "send_email", broken)
    response = client.post("/api/auth/request-code", json={"email": "abc123@psu.edu"})
    assert response.status_code == 502 and response.get_json()["error"]
    assert saved == []
