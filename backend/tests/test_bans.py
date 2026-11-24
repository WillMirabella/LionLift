import random
import string
import threading

import pytest

import bans
import db
from bans import canonical_email

# Tests for bans.py, the email blacklist.
# The canonical_email tests run anywhere; the rest use the test database.


# ---- canonical_email ----

@pytest.mark.parametrize("raw", [
    "abc123@psu.edu", "ABC123@PSU.EDU", "  abc123@psu.edu\t", "abc123+rides@psu.edu",
    "abc123+a+b@psu.edu", "Abc123+X@Psu.Edu ",
    "ａbc123@psu.edu",          # full-width a, folded to a plain a
])
def test_aliases_collapse(raw):
    assert canonical_email(raw) == "abc123@psu.edu"


@pytest.mark.parametrize("raw", [
    "abc@gmail.com", "abc@psu.edu.evil.com", "abc@notpsu.edu", "abc@iot.psu.edu",
    "abc", "", "@psu.edu", "+tag@psu.edu", "a b@psu.edu", "a@b@psu.edu",
    "ab\nc@psu.edu", "ab\tc@psu.edu", "ab\u0000c@psu.edu",
    "аbc@psu.edu",             # Cyrillic a, looks the same as a plain a
    ".abc@psu.edu", None, 123,
])
def test_rejected(raw):
    with pytest.raises(ValueError):
        canonical_email(raw)


# canonical(canonical(x)) == canonical(x), over thousands of random inputs
def test_idempotent():
    rng = random.Random(52)
    alphabet = string.ascii_letters + string.digits + " +-._%@\t"
    checked = 0
    for _ in range(3000):
        raw = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 16))) + rng.choice(["@psu.edu", "@PSU.EDU", ""])
        try:
            once = canonical_email(raw)
        except ValueError:
            continue
        assert canonical_email(once) == once
        checked += 1
    assert checked > 100


def test_invalid_email_is_never_banned():
    # No database call happens for these, so this runs anywhere
    assert bans.is_banned("abc@gmail.com") is False
    assert bans.is_banned(None) is False


# ---- banning, against the test database ----

@pytest.mark.db
@pytest.mark.parametrize("attempt", ["abc123@psu.edu", "ABC123@psu.edu", "abc123+new@psu.edu", " Abc123+X@PSU.EDU "])
def test_ban_covers_every_spelling(attempt):
    bans.ban_email("abc123@psu.edu", "harassment")
    assert bans.is_banned(attempt)


@pytest.mark.db
def test_other_people_are_not_banned():
    bans.ban_email("abc123@psu.edu", "harassment")
    assert not bans.is_banned("abc1234@psu.edu")
    assert not bans.is_banned("xyz789@psu.edu")


@pytest.mark.db
def test_ban_details():
    ban = bans.ban_email("ABC123+x@psu.edu", "  no-shows  ")
    assert ban["email"] == "abc123@psu.edu"
    assert ban["reason"] == "no-shows"
    assert ban["expires_at"] is None and ban["created_at"]
    assert bans.get_ban("abc123@psu.edu") == ban


@pytest.mark.db
def test_unban():
    bans.ban_email("abc123@psu.edu", "spam")
    assert bans.unban_email("ABC123+x@psu.edu") is True
    assert not bans.is_banned("abc123@psu.edu")
    assert bans.unban_email("abc123@psu.edu") is False


@pytest.mark.db
def test_timed_ban_ends():
    bans.ban_email("abc123@psu.edu", "spam", days=30)
    assert bans.is_banned("abc123@psu.edu")

    # Move the end date into the past
    conn = db.get_connection()
    conn.cursor().execute("UPDATE banned_emails SET expires_at = NOW() - INTERVAL '1 second';")
    conn.commit()
    conn.close()

    assert not bans.is_banned("abc123@psu.edu")
    assert bans.get_ban("abc123@psu.edu") is None
    assert bans.list_bans() == []


@pytest.mark.db
def test_banning_again_replaces_reason_and_end():
    bans.ban_email("abc123@psu.edu", "spam", days=7)
    ban = bans.ban_email("abc123@psu.edu", "harassment")
    assert ban["reason"] == "harassment" and ban["expires_at"] is None
    assert len(bans.list_bans()) == 1


@pytest.mark.db
def test_list_bans_newest_first():
    for email in ("aaa1@psu.edu", "bbb2@psu.edu", "ccc3@psu.edu"):
        bans.ban_email(email, "spam")
    assert [ban["email"] for ban in bans.list_bans()] == ["ccc3@psu.edu", "bbb2@psu.edu", "aaa1@psu.edu"]


@pytest.mark.db
def test_long_reason_is_cut():
    assert len(bans.ban_email("abc123@psu.edu", "x" * 900)["reason"]) == bans.MAX_REASON_LENGTH


@pytest.mark.db
@pytest.mark.parametrize("email, reason, days", [
    ("abc@gmail.com", "spam", None),
    ("abc123@psu.edu", "", None),
    ("abc123@psu.edu", "   ", None),
    ("abc123@psu.edu", None, None),
    ("abc123@psu.edu", "spam", 0),
    ("abc123@psu.edu", "spam", -3),
    ("abc123@psu.edu", "spam", 3651),
    ("abc123@psu.edu", "spam", 2.5),
    ("abc123@psu.edu", "spam", "30"),
    ("abc123@psu.edu", "spam", True),
])
def test_ban_rejects_bad_input(email, reason, days):
    with pytest.raises(ValueError):
        bans.ban_email(email, reason, days)
    assert bans.list_bans() == []


# Two admins banning the same person at the same moment leaves one ban, no error
@pytest.mark.db
def test_parallel_bans_make_one_ban():
    errors = []
    barrier = threading.Barrier(10)

    def ban(i):
        barrier.wait()
        try:
            bans.ban_email(f"ABC123+{i}@psu.edu", f"reason {i}")
        except Exception as error:
            errors.append(error)

    threads = [threading.Thread(target=ban, args=(i,)) for i in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert [ban["email"] for ban in bans.list_bans()] == ["abc123@psu.edu"]


@pytest.mark.db
def test_ensure_not_banned():
    bans.ensure_not_banned("abc123@psu.edu")
    bans.ban_email("abc123@psu.edu", "spam")
    with pytest.raises(bans.BannedError):
        bans.ensure_not_banned("ABC123+x@psu.edu")


# The table is made by the first ban, so nothing needs to be set up first
@pytest.mark.db
def test_works_before_the_table_exists():
    conn = db.get_connection()
    conn.cursor().execute("DROP TABLE IF EXISTS banned_emails;")
    conn.commit()
    conn.close()
    assert not bans.is_banned("abc123@psu.edu")
    assert bans.list_bans() == []
    assert bans.unban_email("abc123@psu.edu") is False
    bans.ban_email("abc123@psu.edu", "spam")
    assert bans.is_banned("abc123@psu.edu")
