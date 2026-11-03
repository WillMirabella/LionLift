import hashlib
import hmac
import ipaddress
import os
import re
import unicodedata
import uuid

# Turns the different ways a person can identify themselves into one canonical
# form each, so a ban matches the person and not just the exact text they typed.
#
# Every canonical_* function is idempotent: canonical_x(canonical_x(v)) == canonical_x(v).
# Each raises ValueError when the value can't be used.
#
# canonical_email and client_ip_bucket are the two hooks the alias and IP work
# plugs into. Everything else in the ban system only calls those names.

ALLOWED_EMAIL_DOMAIN = "psu.edu"

# Kinds of identifiers. Strong ones identify one person and block on a match;
# weak ones can be shared (roommates, campus Wi-Fi) and only flag for review.
STRONG_KINDS = ("email", "phone")
WEAK_KINDS = ("device", "payment", "ip")
KINDS = STRONG_KINDS + WEAK_KINDS

# Letters, digits and . _ % + - before the @, which covers PSU Access IDs
EMAIL_PATTERN = re.compile(r"([a-z0-9][a-z0-9._%+-]*)@([a-z0-9.-]+)")

# Secret used to hash identifiers before they're stored, so a leaked database
# doesn't expose banned students' emails or phone numbers.
# Production must set LIONLIFT_BAN_SECRET; the fallback is for development only.
_DEV_SECRET = "lionlift-development-secret-change-me"


# Returns the hashing secret as bytes
def _secret():
    return os.environ.get("LIONLIFT_BAN_SECRET", _DEV_SECRET).encode()


# Maps an alias local part to the person's Access ID. Replace this with the
# real alias resolution; by default the local part is already the identity.
def resolve_alias(local_part):
    return local_part


# Canonical PSU email: Unicode normalized, trimmed, lowercased, +tag removed,
# alias resolved. Lookalike characters and control characters are rejected.
def canonical_email(raw):
    if not isinstance(raw, str):
        raise ValueError("email must be text")

    email = unicodedata.normalize("NFKC", raw).strip().lower()

    # Non-ASCII here means lookalike letters, e.g. a Cyrillic "а"
    if not email.isascii():
        raise ValueError("email must only use plain letters and digits")

    match = EMAIL_PATTERN.fullmatch(email)
    if not match:
        raise ValueError("not a valid email address")

    local, domain = match.groups()
    if domain != ALLOWED_EMAIL_DOMAIN:
        raise ValueError(f"email must end in @{ALLOWED_EMAIL_DOMAIN}")

    # abc123+anything@psu.edu delivers to abc123@psu.edu
    local = local.split("+", 1)[0]
    if not local:
        raise ValueError("not a valid email address")

    local = resolve_alias(local)
    return f"{local}@{domain}"


# Canonical phone in E.164 form, e.g. +12155550100.
# Ten digits are taken as a US number.
def canonical_phone(raw):
    if not isinstance(raw, str):
        raise ValueError("phone must be text")

    text = unicodedata.normalize("NFKC", raw).strip()
    digits = "".join(ch for ch in text if ch.isdigit())

    if text.startswith("+") and 8 <= len(digits) <= 15:
        return "+" + digits
    if len(digits) == 10:
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    raise ValueError("not a valid phone number")


# Canonical payment handle, e.g. "@Jane-Doe " -> "jane-doe"
def canonical_payment(raw):
    if not isinstance(raw, str):
        raise ValueError("payment handle must be text")

    handle = unicodedata.normalize("NFKC", raw).strip().lower().lstrip("@$")
    handle = "".join(handle.split())
    if not handle or not handle.isascii():
        raise ValueError("not a valid payment handle")
    return handle


# Canonical device id: the random UUID the app creates once per install
def canonical_device(raw):
    if not isinstance(raw, str):
        raise ValueError("device id must be text")
    try:
        return str(uuid.UUID(raw.strip()))
    except ValueError:
        raise ValueError("device id must be a UUID")


# Groups an IP address into the range one person can easily move around in:
# /24 for IPv4 and /64 for IPv6. Also accepts a range it already produced.
def ip_bucket(raw):
    if not isinstance(raw, str):
        raise ValueError("IP address must be text")

    text = raw.strip()
    try:
        address = ipaddress.ip_address(text.split("/")[0])
    except ValueError:
        raise ValueError("not a valid IP address")

    # IPv4 written inside IPv6, e.g. ::ffff:10.0.0.1
    if address.version == 6 and address.ipv4_mapped:
        address = address.ipv4_mapped

    prefix = 24 if address.version == 4 else 64
    return str(ipaddress.ip_network(f"{address}/{prefix}", strict=False))


# The client's IP range for a Flask request. Behind a proxy, wrap the app in
# werkzeug.middleware.proxy_fix.ProxyFix so remote_addr is the real client.
def client_ip_bucket(request):
    if not request.remote_addr:
        return None
    try:
        return ip_bucket(request.remote_addr)
    except ValueError:
        return None


CANONICALIZERS = {
    "email": canonical_email,
    "phone": canonical_phone,
    "payment": canonical_payment,
    "device": canonical_device,
    "ip": ip_bucket,
}


# Canonical form of any kind of identifier
def canonical(kind, raw):
    if kind not in CANONICALIZERS:
        raise ValueError(f"unknown identifier kind {kind!r}")
    return CANONICALIZERS[kind](raw)


# Keyed hash of a canonical identifier, the only form that's stored.
# The kind is part of the input so an email and a phone can never collide.
def hashed(kind, canonical_value):
    return hmac.new(_secret(), f"{kind}:{canonical_value}".encode(), hashlib.sha256).hexdigest()


# Short masked version for admins, e.g. "ab***@psu.edu" or "***0100"
def hint(kind, canonical_value):
    if kind == "email":
        local, _, domain = canonical_value.partition("@")
        return f"{local[:2]}***@{domain}"
    if kind == "phone":
        return "***" + canonical_value[-4:]
    if kind == "ip":
        return canonical_value
    return canonical_value[:3] + "***"
