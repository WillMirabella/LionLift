from datetime import datetime, timedelta, timezone

from psycopg2.extras import Json

import db
import identity

# Blacklist: bans a person by every identifier they're known by.
#
# A ban has one or more identifiers (email, phone, device, payment handle, IP range),
# each stored only as a keyed hash of its canonical form (see identity.py).
# check_identity compares a set of identifiers against all active bans:
#   - any strong match (email or phone) blocks
#   - weak matches add up a score: device 0.6, payment 0.5, IP range 0.2
#   - a score of 0.6 or more is flagged for an admin to review, but allowed
#
# A ban is active when it hasn't been revoked and hasn't expired.

ALLOW = "allow"
REVIEW = "review"
BLOCK = "block"

WEIGHTS = {"device": 0.6, "payment": 0.5, "ip": 0.2}
REVIEW_THRESHOLD = 0.6

ACTIVE = "b.revoked_at IS NULL AND (b.expires_at IS NULL OR b.expires_at > NOW())"


# Raised when a banned person tries to sign up or change their details
class BannedError(Exception):
    pass


# Canonicalizes (kind, raw value) pairs. Missing values are skipped.
# With strict=False, values that can't be read are skipped too instead of raising.
def _canonical_pairs(identifiers, strict=True):
    pairs = []
    for kind, raw in identifiers:
        if raw is None or raw == "":
            continue
        try:
            pairs.append((kind, identity.canonical(kind, raw)))
        except ValueError:
            if strict:
                raise
    return list(dict.fromkeys(pairs))


# Writes one row to the audit log using an open cursor
def _log(curr, ban_id, action, actor=None, detail=None):
    curr.execute(
        "INSERT INTO ban_events (ban_id, action, actor, detail) VALUES (%s, %s, %s, %s);",
        (ban_id, action, actor, Json(detail) if detail is not None else None),
    )


# Checks identifiers against active bans. Returns (decision, matches), where
# matches is a list of (kind, ban_id). Blocked and flagged attempts are logged
# unless record is False.
def check_identity(identifiers, context=None, strict=False, record=True):
    pairs = _canonical_pairs(identifiers, strict)
    if not pairs:
        return ALLOW, []

    hashes = {identity.hashed(kind, value): kind for kind, value in pairs}

    conn = db.get_connection()
    try:
        curr = conn.cursor()
        curr.execute(
            f"""
            SELECT DISTINCT bi.kind, b.id
            FROM ban_identifiers bi JOIN bans b ON b.id = bi.ban_id
            WHERE bi.value = ANY(%s) AND {ACTIVE}
            ORDER BY b.id, bi.kind;
            """,
            (list(hashes),),
        )
        matches = curr.fetchall()

        kinds = {kind for kind, _ in matches}
        if kinds & set(identity.STRONG_KINDS):
            decision = BLOCK
        elif sum(WEIGHTS.get(kind, 0) for kind in kinds) >= REVIEW_THRESHOLD - 1e-9:
            decision = REVIEW
        else:
            decision = ALLOW

        # Record the attempt against each matching ban
        if decision != ALLOW and record:
            action = "blocked_attempt" if decision == BLOCK else "evasion_flagged"
            for ban_id in sorted({ban_id for _, ban_id in matches}):
                matched = sorted(kind for kind, other in matches if other == ban_id)
                _log(curr, ban_id, action, detail={"matched": matched, "context": context})
            conn.commit()
        return decision, matches
    finally:
        conn.close()


# Raises BannedError if the identifiers are blocked. Returns the decision otherwise.
def ensure_allowed(identifiers, context=None):
    decision, _ = check_identity(identifiers, context)
    if decision == BLOCK:
        raise BannedError("this account can't be used")
    return decision


# Identifiers on file for a user: their email and phone.
# preferred_payment holds a payment method like "Cash" or "Venmo", not a handle,
# so it isn't used; a handle can still be added to a ban explicitly.
def _user_identifiers(curr, user_id):
    curr.execute("SELECT email, phone FROM users WHERE id = %s;", (user_id,))
    row = curr.fetchone()
    if row is None:
        raise ValueError(f"no user with id {user_id}")
    email, phone = row
    return [("email", email), ("phone", phone)]


# Bans a person. Give a user_id, identifiers like [("email", "abc@psu.edu")], or both.
# Returns the ban id. If the user already has an active ban, returns that one instead.
# Everything happens in one transaction.
def create_ban(reason, created_by, user_id=None, identifiers=(), duration_days=None):
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("a reason is required")
    if not isinstance(created_by, str) or not created_by.strip():
        raise ValueError("created_by is required")
    if duration_days is not None:
        if isinstance(duration_days, bool) or not isinstance(duration_days, (int, float)) or duration_days <= 0:
            raise ValueError("duration_days must be a positive number")

    explicit = _canonical_pairs(identifiers, strict=True)

    conn = db.get_connection()
    try:
        curr = conn.cursor()

        pairs = list(explicit)
        if user_id is not None:
            # Serialize bans for the same user so two admins can't double-ban
            curr.execute("SELECT pg_advisory_xact_lock(%s);", (int(user_id),))
            curr.execute(f"SELECT b.id FROM bans b WHERE b.user_id = %s AND {ACTIVE};", (user_id,))
            existing = curr.fetchone()
            if existing:
                conn.rollback()
                return existing[0]
            stored = _canonical_pairs(_user_identifiers(curr, user_id), strict=False)
            pairs = list(dict.fromkeys(pairs + stored))

        if not pairs:
            raise ValueError("a ban needs at least one usable identifier")

        expires_at = None
        if duration_days is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)

        curr.execute(
            "INSERT INTO bans (user_id, reason, created_by, expires_at) VALUES (%s, %s, %s, %s) RETURNING id;",
            (user_id, reason.strip(), created_by.strip(), expires_at),
        )
        ban_id = curr.fetchone()[0]

        for kind, value in pairs:
            curr.execute(
                """
                INSERT INTO ban_identifiers (ban_id, kind, value, hint) VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
                """,
                (ban_id, kind, identity.hashed(kind, value), identity.hint(kind, value)),
            )

        _log(curr, ban_id, "created", created_by.strip(),
             {"kinds": sorted({kind for kind, _ in pairs}), "expires_at": expires_at.isoformat() if expires_at else None})
        conn.commit()
        return ban_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Revokes a ban. Returns True if it was active, False if it was already revoked
# or doesn't exist. The ban row is kept for the audit history.
def revoke_ban(ban_id, revoked_by):
    if not isinstance(revoked_by, str) or not revoked_by.strip():
        raise ValueError("revoked_by is required")

    conn = db.get_connection()
    try:
        curr = conn.cursor()
        curr.execute(
            "UPDATE bans SET revoked_at = NOW(), revoked_by = %s WHERE id = %s AND revoked_at IS NULL RETURNING id;",
            (revoked_by.strip(), ban_id),
        )
        revoked = curr.fetchone() is not None
        if revoked:
            _log(curr, ban_id, "revoked", revoked_by.strip())
        conn.commit()
        return revoked
    finally:
        conn.close()


# Turns a bans row into a dict, with its identifiers as masked hints only
def _ban_dict(curr, row):
    ban_id, user_id, reason, created_by, created_at, expires_at, revoked_at, revoked_by, active = row
    curr.execute("SELECT kind, hint FROM ban_identifiers WHERE ban_id = %s ORDER BY kind, hint;", (ban_id,))
    return {
        "id": ban_id,
        "user_id": user_id,
        "reason": reason,
        "created_by": created_by,
        "created_at": created_at.isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "revoked_at": revoked_at.isoformat() if revoked_at else None,
        "revoked_by": revoked_by,
        "active": active,
        "identifiers": [{"kind": kind, "hint": h} for kind, h in curr.fetchall()],
    }


BAN_COLUMNS = f"b.id, b.user_id, b.reason, b.created_by, b.created_at, b.expires_at, b.revoked_at, b.revoked_by, ({ACTIVE})"


# Returns one ban with its audit history, or None
def get_ban(ban_id):
    conn = db.get_connection()
    try:
        curr = conn.cursor()
        curr.execute(f"SELECT {BAN_COLUMNS} FROM bans b WHERE b.id = %s;", (ban_id,))
        row = curr.fetchone()
        if row is None:
            return None
        ban = _ban_dict(curr, row)
        curr.execute("SELECT action, actor, detail, at FROM ban_events WHERE ban_id = %s ORDER BY id;", (ban_id,))
        ban["events"] = [
            {"action": action, "actor": actor, "detail": detail, "at": at.isoformat()}
            for action, actor, detail, at in curr.fetchall()
        ]
        return ban
    finally:
        conn.close()


# Returns bans, newest first. Only active ones unless include_inactive is True.
def list_bans(include_inactive=False):
    conn = db.get_connection()
    try:
        curr = conn.cursor()
        where = "" if include_inactive else f"WHERE {ACTIVE}"
        curr.execute(f"SELECT {BAN_COLUMNS} FROM bans b {where} ORDER BY b.id DESC;")
        return [_ban_dict(curr, row) for row in curr.fetchall()]
    finally:
        conn.close()


# Returns True if the user has an active ban, either directly or through
# their email or phone matching someone else's ban
def is_user_banned(user_id):
    conn = db.get_connection()
    try:
        curr = conn.cursor()
        curr.execute(f"SELECT 1 FROM bans b WHERE b.user_id = %s AND {ACTIVE};", (user_id,))
        if curr.fetchone():
            return True
        try:
            identifiers = _user_identifiers(curr, user_id)
        except ValueError:
            return False
    finally:
        conn.close()
    decision, _ = check_identity(identifiers, record=False)
    return decision == BLOCK


# Moves entries from the old single-column blacklist table, if it exists, into
# permanent email bans. Safe to run more than once. Returns how many were added.
def migrate_legacy_blacklist(created_by="migration"):
    conn = db.get_connection()
    try:
        curr = conn.cursor()
        curr.execute("SELECT to_regclass('public.blacklist');")
        if curr.fetchone()[0] is None:
            return 0
        curr.execute("SELECT email FROM blacklist;")
        emails = [row[0] for row in curr.fetchall()]
    finally:
        conn.close()

    added = 0
    for raw in emails:
        try:
            email = identity.canonical_email(raw)
        except (ValueError, TypeError):
            continue
        decision, _ = check_identity([("email", email)], record=False)
        if decision == BLOCK:
            continue
        create_ban("Migrated from the old blacklist", created_by, identifiers=[("email", email)])
        added += 1
    return added
