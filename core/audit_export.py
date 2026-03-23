"""
Export a machine-readable **audit trail** snapshot from the local SQLite database.

Used by CLI ``--export-audit-trail`` for governance: wipe history, session summary,
and (when implemented) build integrity anchor rows — see
``docs/plans/PLAN_BUILD_IDENTITY_RELEASE_INTEGRITY.md`` Phase E.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from core.about import get_about_info
from core.runtime_trust import get_runtime_trust_snapshot

# Bump when JSON shape changes in a breaking way.
AUDIT_TRAIL_SCHEMA_VERSION = 1


def _iso_utc(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def build_audit_trail_payload(
    db_manager: Any,
    *,
    config: dict[str, Any],
    config_path: str,
    sqlite_path: str,
) -> dict[str, Any]:
    """
    Build a JSON-serializable dict for export.

    Parameters
    ----------
    db_manager
        ``LocalDBManager`` instance (typed as Any to avoid circular imports).
    config_path
        Path to the config file used for this invocation.
    sqlite_path
        Resolved SQLite path from config.
    """
    about = get_about_info()
    runtime_trust = get_runtime_trust_snapshot(config)
    wipe_rows = db_manager.list_data_wipe_log_entries()
    session_summary = db_manager.get_scan_sessions_summary()

    payload: dict[str, Any] = {
        "schema_version": AUDIT_TRAIL_SCHEMA_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "application": {
            "name": about["name"],
            "version": about["version"],
            "author": about["author"],
            "license": about["license"],
        },
        "paths": {
            "config": config_path,
            "sqlite": sqlite_path,
        },
        "runtime_trust": runtime_trust,
        "data_wipe_log": wipe_rows,
        "scan_sessions_summary": session_summary,
        # Populated when PLAN_BUILD_IDENTITY Phase E ships (integrity anchor,
        # per-run integrity events).
        "integrity_anchor": None,
        "integrity_events": None,
        "notes": (
            "integrity_anchor and integrity_events are reserved for "
            "PLAN_BUILD_IDENTITY_RELEASE_INTEGRITY Phase E. "
            "data_wipe_log rows are append-only and are never removed by "
            "wipe_all_data() / --reset-data. "
            "runtime_trust marks if this execution context looked unexpected."
        ),
    }
    return payload
