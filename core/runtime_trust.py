"""
Runtime trust snapshot helpers used by CLI messages and audit exports.
"""

from __future__ import annotations

from typing import Any

from core.licensing import get_license_guard

_UNEXPECTED_LICENSE_STATES = {
    "TAMPERED",
    "INVALID",
    "REVOKED",
    "UNLICENSED",
    "MACHINE_MISMATCH",
    "EXPIRED",
    "CRACKED",
}


def get_runtime_trust_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """
    Return a compact runtime trust snapshot for operator/audit surfaces.
    """
    guard = get_license_guard(config)
    ctx = guard.context
    state = (ctx.state or "UNKNOWN").upper()
    is_unexpected = state in _UNEXPECTED_LICENSE_STATES
    level = "unexpected" if is_unexpected else "expected"
    attention = (
        "THERE IS SOMETHING DIFFERENT AND UNEXPECTED IN THIS RUNTIME."
        if is_unexpected
        else "Runtime looks consistent with expected license/integrity state."
    )
    return {
        "trust_level": level,
        "is_unexpected": is_unexpected,
        "attention": attention,
        "license_state": state,
        "license_mode": ctx.mode,
        "license_detail": ctx.detail,
        "watermark": ctx.watermark,
    }
