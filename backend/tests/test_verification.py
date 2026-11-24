import hashlib

import pytest

from services import verification
from services.verification import check_code, hash_code, is_psu_email, make_code, normalize_email

# Tests for services/verification.py


@pytest.mark.parametrize("raw, expected", [
    ("abc123@psu.edu", "abc123@psu.edu"),
    ("  ABC123@PSU.edu ", "abc123@psu.edu"),
    ("\tAbC@Psu.Edu\n", "abc@psu.edu"),
])
def test_normalize_email(raw, expected):
    assert normalize_email(raw) == expected


@pytest.mark.parametrize("email", ["abc123@psu.edu", "a@psu.edu", "first.last@psu.edu"])
def test_accepts_psu_addresses(email):
    assert is_psu_email(email)


@pytest.mark.parametrize("email", [
    "abc@gmail.com", "abc@notpsu.edu", "abc@psu.edu.evil.com", "abc@iot.psu.edu",
    "@psu.edu", "abc", "", "a@b@psu.edu", "a b@psu.edu", "abc@PSU.EDU",
])
def test_rejects_other_addresses(email):
    assert not is_psu_email(email)


# Known gap: control characters inside the address aren't rejected
@pytest.mark.xfail(reason="line breaks and tabs inside the address are accepted")
@pytest.mark.parametrize("email", ["ab\nc@psu.edu", "ab\tc@psu.edu"])
def test_rejects_control_characters(email):
    assert not is_psu_email(email)


def test_settings():
    assert verification.ALLOWED_DOMAIN == "psu.edu"
    assert verification.CODE_EXPIRY_MINUTES == 10
    assert verification.MAX_ATTEMPTS == 5
    assert verification.RESEND_COOLDOWN_SECONDS == 60


def test_hash_code_is_sha256():
    assert hash_code("123456") == hashlib.sha256(b"123456").hexdigest()


def test_make_code_format_and_hash():
    for _ in range(200):
        code, code_hash = make_code()
        assert len(code) == 6 and code.isdigit()
        assert code_hash == hash_code(code)


# Small random numbers must still give 6 digits, e.g. 42 -> "000042"
def test_make_code_zero_padded(monkeypatch):
    monkeypatch.setattr(verification.secrets, "randbelow", lambda n: 42)
    assert make_code()[0] == "000042"


def test_make_code_uses_full_range(monkeypatch):
    calls = []
    monkeypatch.setattr(verification.secrets, "randbelow", lambda n: calls.append(n) or 0)
    make_code()
    assert calls == [1_000_000]


def test_check_code():
    code, code_hash = make_code()
    assert check_code(code, code_hash)
    wrong = "000000" if code != "000000" else "111111"
    assert not check_code(wrong, code_hash)
    assert not check_code(code, None)
