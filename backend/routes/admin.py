import hmac
import os
from functools import wraps

from flask import Blueprint, g, jsonify, request

import bans

# Admin API for managing bans.
#
# Every request needs "Authorization: Bearer <token>". Tokens are set per admin in
# the LIONLIFT_ADMIN_TOKENS environment variable, e.g. "ian:longrandomtoken,will:another",
# so every ban records which admin made it. With no tokens set, the admin API is off.
#
# Changes only accept JSON bodies with POST or DELETE. Browsers can't send these
# with an Authorization header from another site, so links and forms can't trigger them.

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

IDENTIFIER_FIELDS = ("email", "phone", "payment", "device")


# Reads "name:token,name:token" into {token: name}, skipping malformed entries
def _load_tokens():
    tokens = {}
    for entry in os.environ.get("LIONLIFT_ADMIN_TOKENS", "").split(","):
        name, _, token = entry.strip().partition(":")
        if name.strip() and len(token.strip()) >= 16:
            tokens[token.strip()] = name.strip()
    return tokens


# Returns the admin name for the request's token, or None
def _admin_for_request():
    header = request.headers.get("Authorization", "")
    scheme, _, given = header.partition(" ")
    if scheme.lower() != "bearer" or not given:
        return None
    # Compare against every token in constant time so timing reveals nothing
    found = None
    for token, name in _load_tokens().items():
        if hmac.compare_digest(token.encode(), given.strip().encode()):
            found = name
    return found


def _error(status, message):
    return jsonify({"error": message}), status


# Rejects requests without a valid admin token
def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not _load_tokens():
            return _error(503, "the admin API is not configured")
        admin = _admin_for_request()
        if admin is None:
            return _error(401, "admin token required")
        g.admin = admin
        return view(*args, **kwargs)
    return wrapper


# Reads the JSON body, rejecting anything that isn't a JSON object
def _json_body():
    if not request.is_json:
        return None
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


# Collects identifiers from {"identifiers": {"email": ..., "phone": ...}}
def _identifiers_from(data):
    given = data.get("identifiers") or {}
    if not isinstance(given, dict):
        raise ValueError("identifiers must be an object")
    unknown = set(given) - set(IDENTIFIER_FIELDS)
    if unknown:
        raise ValueError(f"unknown identifier kinds: {', '.join(sorted(unknown))}")
    return [(kind, given[kind]) for kind in IDENTIFIER_FIELDS if given.get(kind) not in (None, "")]


# POST /api/admin/bans
# body: {"reason": "...", "user_id": 5, "identifiers": {"email": "...", "phone": "..."},
#        "duration_days": 30}   (user_id or identifiers required; no duration = permanent)
@admin_bp.post("/bans")
@require_admin
def create_ban():
    data = _json_body()
    if data is None:
        return _error(415, "send a JSON object")

    user_id = data.get("user_id")
    if user_id is not None and (isinstance(user_id, bool) or not isinstance(user_id, int)):
        return _error(400, "user_id must be a whole number")

    try:
        identifiers = _identifiers_from(data)
        ban_id = bans.create_ban(data.get("reason"), g.admin, user_id=user_id,
                                 identifiers=identifiers, duration_days=data.get("duration_days"))
    except ValueError as error:
        return _error(400, str(error))

    return jsonify(bans.get_ban(ban_id)), 201


# GET /api/admin/bans          active bans
# GET /api/admin/bans?all=1    including expired and revoked
@admin_bp.get("/bans")
@require_admin
def list_bans():
    include_inactive = request.args.get("all") in ("1", "true", "yes")
    return jsonify(bans.list_bans(include_inactive))


# GET /api/admin/bans/<id>   one ban with its audit history
@admin_bp.get("/bans/<int:ban_id>")
@require_admin
def get_ban(ban_id):
    ban = bans.get_ban(ban_id)
    if ban is None:
        return _error(404, "no such ban")
    return jsonify(ban)


# DELETE /api/admin/bans/<id>   revokes the ban; the record is kept
@admin_bp.delete("/bans/<int:ban_id>")
@require_admin
def revoke_ban(ban_id):
    if bans.get_ban(ban_id) is None:
        return _error(404, "no such ban")
    revoked = bans.revoke_ban(ban_id, g.admin)
    return jsonify({"id": ban_id, "revoked": revoked})


# POST /api/admin/check   body: {"identifiers": {...}}
# Shows what decision the system would make, without logging an attempt
@admin_bp.post("/check")
@require_admin
def check():
    data = _json_body()
    if data is None:
        return _error(415, "send a JSON object")
    try:
        decision, matches = bans.check_identity(_identifiers_from(data), strict=True, record=False)
    except ValueError as error:
        return _error(400, str(error))
    return jsonify({"decision": decision, "matches": [{"kind": k, "ban_id": b} for k, b in matches]})
