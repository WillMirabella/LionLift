import random
import string
from types import SimpleNamespace

import pytest

import identity
from identity import (
    canonical, canonical_device, canonical_email, canonical_payment, canonical_phone,
    client_ip_bucket, hashed, hint, ip_bucket,
)

# Tests for identity.py: every way of writing the same identifier must give the
# same canonical value, and canonicalizing twice must change nothing.


# ---- email ----

@pytest.mark.parametrize("raw", [
    "abc123@psu.edu", "ABC123@PSU.EDU", "  abc123@psu.edu\t", "abc123+rides@psu.edu",
    "abc123+a+b@psu.edu", "Abc123+X@Psu.Edu ",
    "ａbc123@psu.edu",           # fullwidth a, folded by NFKC
])
def test_email_aliases_collapse(raw):
    assert canonical_email(raw) == "abc123@psu.edu"


@pytest.mark.parametrize("raw", [
    "abc@gmail.com", "abc@psu.edu.evil.com", "abc@notpsu.edu", "abc@iot.psu.edu",
    "abc", "", "@psu.edu", "+tag@psu.edu", "a b@psu.edu", "a@b@psu.edu",
    "ab\nc@psu.edu", "abc@psu.edu\nx", "ab\u0000c@psu.edu",
    "аbc@psu.edu",              # Cyrillic a, looks identical
    ".abc@psu.edu", None, 123,
])
def test_email_rejected(raw):
    with pytest.raises(ValueError):
        canonical_email(raw)


def test_email_alias_hook(monkeypatch):
    monkeypatch.setattr(identity, "resolve_alias", lambda local: {"jane.doe": "jd5"}.get(local, local))
    assert canonical_email("Jane.Doe+x@psu.edu") == "jd5@psu.edu"
    assert canonical_email("jd5@psu.edu") == "jd5@psu.edu"


# ---- phone ----

@pytest.mark.parametrize("raw", [
    "2155550100", "215-555-0100", "(215) 555-0100", "215.555.0100", " 215 555 0100 ",
    "12155550100", "1-215-555-0100", "+1 215 555 0100", "+12155550100",
])
def test_phone_formats_collapse(raw):
    assert canonical_phone(raw) == "+12155550100"


def test_phone_international():
    assert canonical_phone("+44 20 7946 0958") == "+442079460958"


@pytest.mark.parametrize("raw", ["", "555", "1", "21555501000", "+1234567", "phone", None, 2155550100])
def test_phone_rejected(raw):
    with pytest.raises(ValueError):
        canonical_phone(raw)


# ---- payment, device ----

@pytest.mark.parametrize("raw", ["Jane-Doe", "@jane-doe", " @Jane-Doe ", "$jane-doe", "jane - doe"])
def test_payment_handles_collapse(raw):
    assert canonical_payment(raw) == "jane-doe"


@pytest.mark.parametrize("raw", ["", "@", "  ", "café", None])
def test_payment_rejected(raw):
    with pytest.raises(ValueError):
        canonical_payment(raw)


def test_device_ids():
    value = "6F9619FF-8B86-D011-B42D-00C04FC964FF"
    assert canonical_device(value) == "6f9619ff-8b86-d011-b42d-00c04fc964ff"
    assert canonical_device("{" + value + "}") == canonical_device(value)
    for bad in ("", "not-a-uuid", None):
        with pytest.raises(ValueError):
            canonical_device(bad)


# ---- IP ranges ----

@pytest.mark.parametrize("raw, expected", [
    ("203.0.113.7", "203.0.113.0/24"),
    ("203.0.113.250", "203.0.113.0/24"),
    ("::ffff:203.0.113.7", "203.0.113.0/24"),
    ("2001:db8:1:2:3:4:5:6", "2001:db8:1:2::/64"),
    ("2001:db8:1:2::ffff", "2001:db8:1:2::/64"),
    ("203.0.113.0/24", "203.0.113.0/24"),
])
def test_ip_bucket(raw, expected):
    assert ip_bucket(raw) == expected


@pytest.mark.parametrize("raw", ["", "999.1.1.1", "abc", None])
def test_ip_bucket_rejected(raw):
    with pytest.raises(ValueError):
        ip_bucket(raw)


def test_client_ip_bucket():
    assert client_ip_bucket(SimpleNamespace(remote_addr="198.51.100.9")) == "198.51.100.0/24"
    assert client_ip_bucket(SimpleNamespace(remote_addr=None)) is None
    assert client_ip_bucket(SimpleNamespace(remote_addr="garbage")) is None


# ---- properties ----

def _random_text(rng):
    alphabet = string.ascii_letters + string.digits + " +-.@()_$\t"
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 20)))


# c(c(x)) == c(x) for every kind, over thousands of random inputs
@pytest.mark.parametrize("kind", ["email", "phone", "payment", "ip"])
def test_idempotent(kind):
    rng = random.Random(52)
    samples = {
        "email": lambda: rng.choice(["", " ", "X"]) + _random_text(rng) + rng.choice(["@psu.edu", "@PSU.EDU", ""]),
        "phone": lambda: rng.choice(["", "+", "1"]) + "".join(rng.choice("0123456789 -()") for _ in range(rng.randint(5, 16))),
        "payment": lambda: _random_text(rng),
        "ip": lambda: ".".join(str(rng.randint(0, 260)) for _ in range(4)),
    }
    checked = 0
    for _ in range(3000):
        try:
            once = canonical(kind, samples[kind]())
        except ValueError:
            continue
        assert canonical(kind, once) == once
        checked += 1
    assert checked > 100


def test_unknown_kind():
    with pytest.raises(ValueError):
        canonical("plate", "ABC1234")


# ---- hashing and hints ----

def test_hash_depends_on_kind_and_secret(monkeypatch):
    assert hashed("email", "a@psu.edu") != hashed("payment", "a@psu.edu")
    assert len(hashed("email", "a@psu.edu")) == 64
    before = hashed("email", "a@psu.edu")
    monkeypatch.setenv("LIONLIFT_BAN_SECRET", "a different secret")
    assert hashed("email", "a@psu.edu") != before


@pytest.mark.parametrize("kind, value, expected", [
    ("email", "abc123@psu.edu", "ab***@psu.edu"),
    ("phone", "+12155550100", "***0100"),
    ("payment", "jane-doe", "jan***"),
    ("ip", "203.0.113.0/24", "203.0.113.0/24"),
])
def test_hint_masks(kind, value, expected):
    assert hint(kind, value) == expected
