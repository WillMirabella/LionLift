import hashlib
import hmac
import secrets

# Only Penn State emails can sign up
ALLOWED_DOMAIN = "psu.edu"

CODE_EXPIRY_MINUTES = 10
MAX_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60


# Lowercases and trims an email so ABC123@PSU.edu and abc123@psu.edu are the same
# otherwise users could sign up multiple times by changing capitalization
def normalize_email(email):
    return email.strip().lower()


# Checks that the email is exactly <something>@psu.edu
# (an exact match, so notpsu.edu or psu.edu.fake.com are rejected)
# (this also means @iot.psu.edu would not work if the school administers emails like that)
def is_psu_email(email):
    local, at, domain = email.rpartition("@")
    if at == "" or local == "" or "@" in local or " " in email:
        return False
    return domain == ALLOWED_DOMAIN


def hash_code(code):
    return hashlib.sha256(code.encode()).hexdigest()


# Makes a random 6-digit code, returns (code, hash of code)
def make_code():
    code = f"{secrets.randbelow(1_000_000):06d}"
    return code, hash_code(code)


# Checks a code the user typed against the stored hash
def check_code(code, code_hash):
    if code_hash is None:
        return False
    return hmac.compare_digest(hash_code(code), code_hash)
