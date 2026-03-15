"""
Input validation helpers for security hardening.

Used for tenant/technician and other operator-supplied values that are stored
or displayed in reports/UI. Keeps values within length limits and strips
control characters to reduce abuse and injection risk.
"""
# Match DB column size (core.database.ScanSession.tenant_name / technician_name)
MAX_TENANT_TECHNICIAN_LENGTH = 255


def sanitize_tenant_technician(value: str | None, max_length: int = MAX_TENANT_TECHNICIAN_LENGTH) -> str | None:
    """
    Sanitize an optional tenant or technician string for storage and display.

    - Strips leading/trailing whitespace.
    - Removes ASCII control characters (ord < 32 and DEL 0x7f) to avoid
      injection or broken rendering in Excel/HTML.
    - Truncates to max_length (default 255, matching DB column) so we never
      overflow the database.

    Returns None if the result is empty after sanitization.
    """
    if value is None:
        return None
    s = value.strip()
    if not s:
        return None
    # Allow only printable / safe chars: drop control chars (0x00-0x1f, 0x7f)
    sanitized = "".join(c for c in s if ord(c) >= 32 and ord(c) != 127)
    sanitized = sanitized.strip()
    if not sanitized:
        return None
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    return sanitized


def redact_secrets_for_log(text: str | None) -> str:
    """
    Return a copy of text safe for logging: mask passwords, API keys, connection URLs
    with credentials, and similar secrets. Used for failure details and any log message
    that might contain config or exception content.
    """
    if not text:
        return ""
    import re
    out = text
    # Connection URL with user:password@ (e.g. postgresql://u:secret@host/db)
    out = re.sub(r"([a-z][a-z0-9+.-]*://)([^@\s]+)(@[^\s]+)", r"\1***REDACTED***\3", out, flags=re.IGNORECASE)
    # password=, pass=, api_key=, client_secret=, token= (key=value)
    out = re.sub(
        r"(password|pass|api_key|client_secret|token)(\s*=\s*)([^\s&]+)",
        r"\1\2***REDACTED***",
        out,
        flags=re.IGNORECASE,
    )
    return out
