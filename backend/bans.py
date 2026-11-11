import re
import unicodedata
from datetime import datetime, timedelta, timezone

import psycopg2

import db
from services.verification import is_psu_email, normalize_email

# Email bans for the blacklist (issue #52).
#
# Email is the only thing the backend verifies about a person, so it is what a
# ban is attached to. A ban covers every way of writing the same Penn State
# email: capital letters, extra spaces, look-alike characters and +tags.

# Characters allowed before the @, after any +tag is removed
_LOCAL_PART = re.compile(r"[a-z0-9][a-z0-9._%-]*")

# Longest a timed ban can be, about 10 years
MAX_BAN_DAYS = 3650

# Longest reason that is stored
MAX_REASON_LENGTH = 500

# The bans table. It lives here instead of in db.create_relations so the
# blacklist is self-contained, and it is created the first time a ban is saved.
CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS banned_emails (
        email VARCHAR(254) PRIMARY KEY,
        reason VARCHAR(500) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        expires_at TIMESTAMPTZ
    );
"""

# Columns every query returns, in this order
COLUMNS = "email, reason, created_at, expires_at"

# A ban counts while it has no end date or its end date hasn't passed
ACTIVE = "(expires_at IS NULL OR expires_at > NOW())"


class BannedError(Exception):
    pass


# Returns the one canonical form of a Penn State email, or raises ValueError.
# Every way of writing the same inbox gives the same result, and running it
# again on its own result changes nothing.
def canonical_email(email):
    if not isinstance(email, str):
        raise ValueError("email must be text")

    # Full-width and other compatibility characters become their plain versions
    email = normalize_email(unicodedata.normalize("NFKC", email))

    # Look-alike letters from other alphabets (like a Cyrillic a) stay
    # non-ASCII after that, so they are refused instead of matched
    if not email.isascii() or any(ch.isspace() or not ch.isprintable() for ch in email):
        raise ValueError("email has characters that aren't allowed")
    if not is_psu_email(email):
        raise ValueError("email must be a @psu.edu address")

    local, _, domain = email.rpartition("@")

    # abc123+anything@psu.edu is delivered to abc123@psu.edu, so the tag is dropped
    local = local.split("+", 1)[0]
    if not _LOCAL_PART.fullmatch(local):
        raise ValueError("email has an invalid name before the @")

    return f"{local}@{domain}"


# ---- database ----

# Runs one query and returns its rows. If the bans table doesn't exist yet,
# a read returns no rows (nobody has been banned), and a write creates the
# table and tries again.
def _run(query, params=(), write=False):
    conn = db.get_connection()
    try:
        curr = conn.cursor()
        try:
            curr.execute(query, params)
        except psycopg2.errors.UndefinedTable:
            conn.rollback()
            if not write:
                return []
            _create_table(conn)
            curr = conn.cursor()
            curr.execute(query, params)
        rows = curr.fetchall() if curr.description else []
        conn.commit()
        return rows
    finally:
        conn.close()


# Creates the bans table. Two requests creating it at the same moment can
# collide inside Postgres; the loser just uses the table the winner made.
def _create_table(conn):
    try:
        conn.cursor().execute(CREATE_TABLE)
        conn.commit()
    except (psycopg2.errors.UniqueViolation, psycopg2.errors.DuplicateTable):
        conn.rollback()


def _save_ban(email, reason, expires_at):
    return _run(f"""
        INSERT INTO banned_emails (email, reason, expires_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO UPDATE
        SET reason = EXCLUDED.reason, expires_at = EXCLUDED.expires_at, created_at = NOW()
        RETURNING {COLUMNS};
    """, (email, reason, expires_at), write=True)[0]


def _active_ban(email):
    rows = _run(f"SELECT {COLUMNS} FROM banned_emails WHERE email = %s AND {ACTIVE};", (email,))
    return rows[0] if rows else None


def _active_bans():
    return _run(f"SELECT {COLUMNS} FROM banned_emails WHERE {ACTIVE} ORDER BY created_at DESC, email;")


def _delete_ban(email):
    return bool(_run("DELETE FROM banned_emails WHERE email = %s RETURNING email;", (email,), write=True))


# ---- checking and managing bans ----

# True if this email, written any way, is banned right now.
# Text that isn't a valid Penn State email can't be banned, so it gives False.
def is_banned(email):
    try:
        email = canonical_email(email)
    except ValueError:
        return False
    return _active_ban(email) is not None


# Raises BannedError if the email is banned. Sign-in and sign-up can call this
# (or is_banned) to turn banned people away.
def ensure_not_banned(email):
    if is_banned(email):
        raise BannedError("this email is banned")


# Bans an email. days=None bans it until it is removed. Banning an email that
# is already banned replaces the reason and end date. Returns the ban.
def ban_email(email, reason, days=None):
    email = canonical_email(email)

    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("a reason is required")
    reason = reason.strip()[:MAX_REASON_LENGTH]

    expires_at = None
    if days is not None:
        # bool is a kind of int in Python, so it's ruled out on its own
        if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= MAX_BAN_DAYS:
            raise ValueError(f"days must be a whole number from 1 to {MAX_BAN_DAYS}")
        expires_at = datetime.now(timezone.utc) + timedelta(days=days)

    return _to_dict(_save_ban(email, reason, expires_at))


# Removes a ban. Returns True if there was one to remove.
def unban_email(email):
    return _delete_ban(canonical_email(email))


# Returns the current ban on an email, or None
def get_ban(email):
    row = _active_ban(canonical_email(email))
    return None if row is None else _to_dict(row)


# Returns every current ban, newest first
def list_bans():
    return [_to_dict(row) for row in _active_bans()]


# Turns a (email, reason, created_at, expires_at) row into a dict for JSON
def _to_dict(row):
    email, reason, created_at, expires_at = row
    return {
        "email": email,
        "reason": reason,
        "created_at": created_at.isoformat(),
        "expires_at": None if expires_at is None else expires_at.isoformat(),
    }
