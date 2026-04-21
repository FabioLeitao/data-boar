"""Unit tests for HTML CSRF tokens (WebAuthn Phase 1b)."""

from core.webauthn_rp.html_csrf import issue_html_csrf_token, verify_html_csrf_token


def test_issue_and_verify_roundtrip():
    secret = "test-secret-minimum-16-chars"
    tok = issue_html_csrf_token(secret)
    assert verify_html_csrf_token(secret, tok) is True


def test_verify_rejects_tampered():
    secret = "test-secret-minimum-16-chars"
    tok = issue_html_csrf_token(secret)
    assert verify_html_csrf_token(secret, tok[:-3] + "xxx") is False


def test_verify_rejects_wrong_secret():
    tok = issue_html_csrf_token("secret-a______________")
    assert verify_html_csrf_token("secret-b______________", tok) is False
