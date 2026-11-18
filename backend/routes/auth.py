import db
from models.user import User

import re
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, request, current_app
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, decode_token, get_jwt, verify_jwt_in_request
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

bcrypt = Bcrypt()
jwt = JWTManager()

# How long the user has after entering a code to actually set their password
SIGNUP_TOKEN_MINUTES = 15
RESET_TOKEN_MINUTES = 10


# Checks a password against our rules, returns an error message or None if it's fine
# Keep these in sync with the checklist in frontend/app/set-password.tsx
def password_error(password):
    if not isinstance(password, str) or len(password) < 8:
        return "Password must be at least 8 characters long"
    if not (re.search(r"[A-Za-z]", password) and re.search(r"\d", password)):
        return "Password must contain letters and numbers"
    if not (re.search(r"[a-z]", password) and re.search(r"[A-Z]", password)):
        return "Password must contain upper and lower case"
    if not re.search(r"[^a-zA-Z0-9 ]", password):
        return "Password must contain a special character ($, !, @, #)"
    return None


# Makes a short-lived token that only works for one step (purpose is "signup" or "reset")
def make_purpose_token(email, purpose, minutes):
    return create_access_token(
        identity=email,
        additional_claims={"purpose": purpose},
        expires_delta=timedelta(minutes=minutes),
    )


# Reads the "Authorization: Bearer <token>" header and returns the token's claims
# if it's valid and was made for this purpose, otherwise None
def get_purpose_claims(purpose):
    try:
        verify_jwt_in_request()
    except Exception:
        return None
    claims = get_jwt()
    if claims.get("purpose") != purpose:
        return None
    return claims

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

    now = datetime.now(timezone.utc)
    record = db.get_verification(email)
    if record is not None:
        code_hash, expires_at, attempts, last_sent_at, verified = record
        # verified but no account means they never finished signing up, so let them get a new code
        if verified and db.get_user_by_email(email):
            return jsonify({"status": "already_verified"}), 200
        if last_sent_at is not None and now - last_sent_at < timedelta(seconds=RESEND_COOLDOWN_SECONDS):
            return jsonify({"error": "Please wait a minute before requesting another code"}), 429

    code, code_hash = make_code()
    # send before saving, so if the email fails the old code and cooldown are left alone
    try:
        send_email(
            email,
            "Your LionLift verification code",
            f"Your verification code is {code}. It expires in {CODE_EXPIRY_MINUTES} minutes.",
        )
    except Exception as e:
        print(f"Failed to send verification email to {email}: {e}")
        return jsonify({"error": "Couldn't send the verification email, please try again"}), 502

    db.save_verification_code(email, code_hash, now + timedelta(minutes=CODE_EXPIRY_MINUTES))
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
    record = db.get_verification(email)
    if record is None:
        return jsonify({"error": "No code was requested for this email"}), 400

    code_hash, expires_at, attempts, last_sent_at, verified = record
    if code_hash is None:
        return jsonify({"error": "No code was requested for this email"}), 400
    if attempts >= MAX_ATTEMPTS:
        return jsonify({"error": "Too many attempts, please request a new code"}), 400
    if expires_at is None or datetime.now(timezone.utc) > expires_at:
        return jsonify({"error": "Code expired, please request a new one"}), 400

    if not check_code(code.strip(), code_hash):
        db.increment_verification_attempts(email)
        return jsonify({"error": "Incorrect code"}), 400

    db.mark_email_verified(email)
    # set-password needs this token, so only someone who got the code can create the account
    token = make_purpose_token(email, "signup", SIGNUP_TOKEN_MINUTES)
    return jsonify({"status": "verified", "token": token}), 200

# POST /api/auth/set-password   header: Authorization: Bearer <token from /verify>
#                               body: {"password": "..."}
# creates the account for the email the token was issued for, and logs them in
# returns {"status": ..., "token": <login token, same as /login gives>}
@auth_bp.post("/set-password")
def set_password():
    claims = get_purpose_claims("signup")
    if claims is None:
        return jsonify({"error": "Your verification expired, please verify your email again"}), 401
    email = claims["sub"]

    data = request.get_json(silent=True) or {}
    password = data.get("password")
    error = password_error(password)
    if error:
        return jsonify({"error": error}), 400

    if db.get_user_by_email(email):
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    db.insert_user(User(email, hashed_pw))

    # log them in right away so they don't have to sign in after creating their account
    access_token = create_access_token(identity=email)
    return jsonify({"status": "Password set successfully", "token": access_token}), 201


# POST /api/auth/request-reset   body: {"email": "abc123@psu.edu"}
# emails a 6-digit password reset code (also used to resend a code)
# always says code_sent for a valid psu email, so this can't be used to find out who has an account
@auth_bp.post("/request-reset")
def request_reset():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not isinstance(email, str):
        return jsonify({"error": "Email is required"}), 400

    email = normalize_email(email)
    if not is_psu_email(email):
        return jsonify({"error": "Please use your @psu.edu email"}), 400

    if not db.get_user_by_email(email):
        return jsonify({"status": "code_sent"}), 200

    now = datetime.now(timezone.utc)
    record = db.get_reset(email)
    if record is not None:
        last_sent_at = record[3]
        if last_sent_at is not None and now - last_sent_at < timedelta(seconds=RESEND_COOLDOWN_SECONDS):
            return jsonify({"error": "Please wait a minute before requesting another code"}), 429

    code, code_hash = make_code()
    # send before saving, so if the email fails the old code and cooldown are left alone
    try:
        send_email(
            email,
            "Your LionLift password reset code",
            f"Your password reset code is {code}. It expires in {CODE_EXPIRY_MINUTES} minutes.\n\n"
            "If you didn't ask to reset your password, you can ignore this email.",
        )
    except Exception as e:
        print(f"Failed to send reset email to {email}: {e}")
        return jsonify({"error": "Couldn't send the reset email, please try again"}), 502

    db.save_reset_code(email, code_hash, now + timedelta(minutes=CODE_EXPIRY_MINUTES))
    return jsonify({"status": "code_sent"}), 200


# POST /api/auth/verify-reset   body: {"email": "abc123@psu.edu", "code": "123456"}
# checks the reset code and returns a one-time token for /reset-password
@auth_bp.post("/verify-reset")
def verify_reset():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    code = data.get("code")
    if not isinstance(email, str) or not isinstance(code, str):
        return jsonify({"error": "Email and code are required"}), 400

    email = normalize_email(email)
    record = db.get_reset(email)
    if record is None or record[0] is None:
        return jsonify({"error": "No code was requested for this email"}), 400

    code_hash, expires_at, attempts, last_sent_at, token_id = record
    if attempts >= MAX_ATTEMPTS:
        return jsonify({"error": "Too many attempts, please request a new code"}), 400
    if expires_at is None or datetime.now(timezone.utc) > expires_at:
        return jsonify({"error": "Code expired, please request a new one"}), 400

    if not check_code(code.strip(), code_hash):
        db.increment_reset_attempts(email)
        return jsonify({"error": "Incorrect code"}), 400

    token = make_purpose_token(email, "reset", RESET_TOKEN_MINUTES)
    db.mark_reset_code_used(email, decode_token(token)["jti"])
    return jsonify({"status": "verified", "token": token}), 200


# POST /api/auth/reset-password   header: Authorization: Bearer <token from /verify-reset>
#                                 body: {"password": "..."}
# sets a new password, the token only works once
@auth_bp.post("/reset-password")
def reset_password():
    claims = get_purpose_claims("reset")
    if claims is None:
        return jsonify({"error": "Your reset expired, please request a new code"}), 401

    data = request.get_json(silent=True) or {}
    password = data.get("password")
    error = password_error(password)
    if error:
        return jsonify({"error": error}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    if not db.reset_password(claims["sub"], claims["jti"], hashed_pw):
        return jsonify({"error": "This reset was already used, please request a new code"}), 400

    return jsonify({"status": "password_reset"}), 200


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Enter an email and password"}), 400

    user = db.get_user_by_email(normalize_email(email))

    # Check the password using Bcrypt
    if user and bcrypt.check_password_hash(user[2], password):
        # Generate an access token for the frontend
        access_token = create_access_token(identity=user[1])
        return jsonify({"token": access_token}), 200

    return jsonify({"error": "Invalid credentials"}), 400
