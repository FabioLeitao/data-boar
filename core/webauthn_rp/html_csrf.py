"""Signed CSRF tokens for HTML form POSTs when WebAuthn HTML session gate is active (#86 Phase 1b)."""

from __future__ import annotations

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

_CSRF_SALT = "html-csrf-v1"
# Short-lived: forms are submitted soon after page load.
_CSRF_MAX_AGE_SECONDS = 3600


def issue_html_csrf_token(secret: str) -> str:
    ser = URLSafeTimedSerializer(secret, salt=_CSRF_SALT)
    return ser.dumps({"v": 1})


def verify_html_csrf_token(secret: str, token: str | None) -> bool:
    if not token or not isinstance(token, str):
        return False
    ser = URLSafeTimedSerializer(secret, salt=_CSRF_SALT)
    try:
        data = ser.loads(token, max_age=_CSRF_MAX_AGE_SECONDS)
        return isinstance(data, dict) and data.get("v") == 1
    except (BadSignature, SignatureExpired, TypeError, ValueError, KeyError):
        return False
