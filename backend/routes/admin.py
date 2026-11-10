from flask import Blueprint, jsonify, request

import bans

# Ban management for admins (issue #52).
#
# These routes only answer requests made on the server itself, the same idea as
# the localhost rule in the first blacklist PR, so they need no passwords or
# tokens. Run the requests from the machine the backend runs on.
admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# Addresses a request has when it comes from the same machine
LOCAL_ADDRESSES = {"127.0.0.1", "::1"}

# Host names a request made on this machine uses
LOCAL_HOSTS = {"localhost", "127.0.0.1", "[::1]"}

# Headers a proxy adds when it passes on someone else's request.
# If any is there, the request didn't really start on this machine.
FORWARDING_HEADERS = ("Forwarded", "X-Forwarded-For", "X-Real-IP")


# Host name without its port, e.g. localhost:5000 -> localhost, [::1]:5000 -> [::1]
def _host_name(host):
    if host.startswith("["):
        return host.split("]", 1)[0] + "]"
    return host.split(":", 1)[0]


# Turns away anything that isn't a direct request from this machine
@admin_bp.before_request
def local_only():
    host = _host_name(request.host).lower()

    # The Host check stops a website from reaching these routes through an
    # admin's browser by pointing its own domain name at 127.0.0.1
    if (request.remote_addr not in LOCAL_ADDRESSES
            or host not in LOCAL_HOSTS
            or any(header in request.headers for header in FORWARDING_HEADERS)):
        # 404, so outsiders can't tell these routes exist
        return jsonify({"error": "Not found"}), 404
    return None


# GET /api/admin/bans
# lists every current ban, newest first
@admin_bp.get("/bans")
def list_bans():
    return jsonify(bans.list_bans())


# POST /api/admin/bans   body: {"email": "abc123@psu.edu", "reason": "...", "days": 30}
# bans an email; leave out days to ban until removed
@admin_bp.post("/bans")
def create_ban():
    # Only JSON, so a form on another website can't post here through a browser
    if not request.is_json:
        return jsonify({"error": "Send the ban as JSON"}), 415

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Body must be a JSON object"}), 400

    try:
        ban = bans.ban_email(data.get("email"), data.get("reason"), data.get("days"))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(ban), 201


# GET /api/admin/bans/abc123@psu.edu
# shows the current ban on an email, if there is one
@admin_bp.get("/bans/<path:email>")
def get_ban(email):
    try:
        ban = bans.get_ban(email)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    if ban is None:
        return jsonify({"error": "This email isn't banned"}), 404
    return jsonify(ban)


# DELETE /api/admin/bans/abc123@psu.edu
# removes the ban on an email
@admin_bp.delete("/bans/<path:email>")
def remove_ban(email):
    try:
        canonical = bans.canonical_email(email)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"email": canonical, "removed": bans.unban_email(canonical)})
