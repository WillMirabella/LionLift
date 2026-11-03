from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

import bans
import db
from identity import client_ip_bucket
from services.email_sender import send_email
from services.verification import (
    CODE_EXPIRY_MINUTES,
    MAX_ATTEMPTS,
    RESEND_COOLDOWN_SECONDS,
    check_code,
    is_psu_email,
    make_code,
    normalize_email,
)

# make a blueprint for email verification
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# Returns True if this email, device or network is banned.
# The app sends its install id in the X-Device-Id header.
def _blocked(email, context):
    decision, _ = bans.check_identity([
        ("email", email),
        ("device", request.headers.get("X-Device-Id")),
        ("ip", client_ip_bucket(request)),
    ], context=context)
    return decision == bans.BLOCK


# POST /api/auth/request-code   body: {"email": "abc123@psu.edu"}
# emails a 6-digit code to the user (also used to resend a code)
@auth_bp.post("/request-code")
def request_code():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not isinstance(email, str):
        return jsonify({"error": "Email is required"}), 400

    email = normalize_email(email)
    if not is_psu_email(email):
        return jsonify({"error": "Please use your @psu.edu email"}), 400

    # Banned people get the same reply as everyone else, but no code is sent,
    # so the response can't be used to find out who is banned
    if _blocked(email, "request-code"):
        return jsonify({"status": "code_sent"}), 200

    now = datetime.now(timezone.utc)
    record = db.get_verification(email)
    if record is not None:
        code_hash, expires_at, attempts, last_sent_at, verified = record
        if verified:
            return jsonify({"status": "already_verified"}), 200
        if last_sent_at is not None and now - last_sent_at < timedelta(seconds=RESEND_COOLDOWN_SECONDS):
            return jsonify({"error": "Please wait a minute before requesting another code"}), 429

    code, code_hash = make_code()
    db.save_verification_code(email, code_hash, now + timedelta(minutes=CODE_EXPIRY_MINUTES))
    send_email(
        email,
        "Your LionLift verification code",
        f"Your verification code is {code}. It expires in {CODE_EXPIRY_MINUTES} minutes.",
    )
    return jsonify({"status": "code_sent"}), 200


# POST /api/auth/verify   body: {"email": "abc123@psu.edu", "code": "123456"}
# checks the code and marks the email as verified
@auth_bp.post("/verify")
def verify():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    code = data.get("code")
    if not isinstance(email, str) or not isinstance(code, str):
        return jsonify({"error": "Email and code are required"}), 400

    email = normalize_email(email)
    if _blocked(email, "verify"):
        return jsonify({"error": "This email can't be verified"}), 403

    record = db.get_verification(email)
    if record is None:
        return jsonify({"error": "No code was requested for this email"}), 400

    code_hash, expires_at, attempts, last_sent_at, verified = record
    if verified:
        return jsonify({"status": "verified"}), 200
    if attempts >= MAX_ATTEMPTS:
        return jsonify({"error": "Too many attempts, please request a new code"}), 400
    if expires_at is None or datetime.now(timezone.utc) > expires_at:
        return jsonify({"error": "Code expired, please request a new one"}), 400

    if not check_code(code.strip(), code_hash):
        db.increment_verification_attempts(email)
        return jsonify({"error": "Incorrect code"}), 400

    db.mark_email_verified(email)
    return jsonify({"status": "verified"}), 200
