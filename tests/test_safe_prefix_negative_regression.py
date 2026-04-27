"""
Negative regression tests for ``report.safe_prefix.safe_session_prefix``.

Background
----------
Commit ``fd21077`` (``fix(security):``) hardened CodeQL findings around scan
manifest paths by introducing :func:`safe_session_prefix`. The function is the
last defence between an operator-supplied ``session_id`` and the basename of
files written to disk by ``write_scan_evidence_artifacts``.

The original test file (``tests/test_safe_prefix.py``) covers the happy path.
This file proves the **bug cannot return**: each scenario below corresponds to
a class of CodeQL / Bandit-style path-traversal or filename-injection vector
that the fix exists to neutralise.

Per the SDET mission ("the test must reflect real-world stress"), every input
here is a realistic attacker payload, not a synthetic edge case.
"""

from __future__ import annotations

import pytest

from report.safe_prefix import safe_session_prefix


@pytest.mark.parametrize(
    "payload",
    [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "../../../../../../../../tmp/escape",
        "/absolute/etc/shadow",
        "C:\\Users\\Public\\evil.txt",
        "session/../../../../etc/hostname",
    ],
)
def test_no_path_separator_or_parent_traversal_survives(payload: str) -> None:
    """No prefix may contain ``/``, ``\\``, or a literal ``..`` after sanitisation."""
    out = safe_session_prefix(payload, max_len=16)
    assert "/" not in out
    assert "\\" not in out
    assert ".." not in out
    assert ":" not in out


@pytest.mark.parametrize(
    "payload",
    [
        "session\x00../../../etc/passwd",
        "id\nrm -rf /",
        "id\r\nINJECTED",
        "id\t\tweird",
        "lat-\x1bcontrol",
    ],
)
def test_control_bytes_are_stripped(payload: str) -> None:
    """Newlines, tabs, NUL, and ESC must not survive into a filename."""
    out = safe_session_prefix(payload, max_len=16)
    for forbidden in ("\x00", "\n", "\r", "\t", "\x1b"):
        assert forbidden not in out


@pytest.mark.parametrize("payload", ["", "   ", "\t\t", "\n", None])
def test_empty_or_whitespace_falls_back_to_session(payload) -> None:
    """Empty / whitespace / ``None`` must fall back to the documented sentinel."""
    out = safe_session_prefix(payload or "", max_len=16)
    assert out == "session"


def test_only_special_chars_collapse_to_session() -> None:
    """An input made entirely of forbidden characters must not yield ``''``."""
    out = safe_session_prefix("///\\\\!!!@@@", max_len=16)
    assert out
    assert out == "session"


def test_max_len_below_minimum_is_floored() -> None:
    """``max_len < 4`` is silently raised to 4 (documented behaviour)."""
    out = safe_session_prefix("cli-exec-report", max_len=1)
    assert len(out) == 4
    assert "/" not in out


def test_uuid_like_keeps_canonical_shape() -> None:
    """Real UUIDs must keep hex + hyphen (operator-readable trace ids)."""
    uuid = "0123abcd-4567-89ef-cafe-deadbeef1234"
    out = safe_session_prefix(uuid, max_len=18)
    assert out == "0123abcd-4567-89ef"
    assert all(ch in "0123456789abcdef-" for ch in out)


def test_unicode_payload_is_collapsed_to_underscores() -> None:
    """Non-ASCII (emoji / RTL / BIDI tricks) must not survive into a filename."""
    out = safe_session_prefix("rep\u202eorla\u200btxt\U0001f4a3", max_len=16)
    for forbidden in ("\u202e", "\u200b", "\U0001f4a3"):
        assert forbidden not in out
    assert all(ch.isascii() for ch in out)


def test_long_payload_is_truncated_to_max_len() -> None:
    """Truncation must respect ``max_len`` and never leak the rest."""
    payload = "a" * 200 + "/etc/passwd"
    out = safe_session_prefix(payload, max_len=16)
    assert len(out) <= 16
    assert "passwd" not in out


def test_double_dot_only_payload_does_not_collapse_to_dotdot() -> None:
    """``..`` alone must not become a path-traversal token after cleaning."""
    out = safe_session_prefix("..", max_len=8)
    assert out != ".."
    assert ".." not in out


def test_idempotent_when_already_safe() -> None:
    """A clean prefix should pass through unchanged (within max_len)."""
    out = safe_session_prefix("clean-id-01", max_len=16)
    assert out == "clean-id-01"
