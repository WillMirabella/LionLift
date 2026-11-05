from services.email_sender import send_email

# Tests for services/email_sender.py (prints instead of sending for now)


def test_send_email_prints_message(capsys):
    send_email("abc123@psu.edu", "Your code", "Your verification code is 123456.")
    printed = capsys.readouterr().out
    assert "EMAIL to abc123@psu.edu" in printed
    assert "Subject: Your code" in printed
    assert "Your verification code is 123456." in printed


def test_send_email_returns_nothing(capsys):
    assert send_email("a@psu.edu", "s", "b") is None
