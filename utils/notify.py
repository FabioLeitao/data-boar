"""
Off-band and scan-completion notifications (webhooks, Slack, Teams, Telegram).

Default: disabled in config. Secrets come from env or config; never log full URLs.
See docs/USAGE.md and PLAN_NOTIFICATIONS_OFFBAND_AND_SCAN_COMPLETE.md.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

_LOGGER = logging.getLogger("LGPDAudit")

# Phase 3 (Wabbix / PLAN_NOTIFICATIONS): transient webhook failures (5xx, network).
_WEBHOOK_MAX_ATTEMPTS = 3


def _post_json(url: str, payload: dict[str, Any], timeout_s: float = 15.0) -> None:
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(_WEBHOOK_MAX_ATTEMPTS):
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                resp.read()
            return
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt < _WEBHOOK_MAX_ATTEMPTS - 1:
                time.sleep(0.5 * (2**attempt))
                continue
            raise
        except urllib.error.URLError:
            if attempt < _WEBHOOK_MAX_ATTEMPTS - 1:
                time.sleep(0.5 * (2**attempt))
                continue
            raise


def _post_form(url: str, body: dict[str, str], timeout_s: float = 15.0) -> None:
    encoded = urllib.parse.urlencode(body).encode("utf-8")
    for attempt in range(_WEBHOOK_MAX_ATTEMPTS):
        req = urllib.request.Request(
            url,
            data=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                resp.read()
            return
        except urllib.error.HTTPError as e:
            if e.code >= 500 and attempt < _WEBHOOK_MAX_ATTEMPTS - 1:
                time.sleep(0.5 * (2**attempt))
                continue
            raise
        except urllib.error.URLError:
            if attempt < _WEBHOOK_MAX_ATTEMPTS - 1:
                time.sleep(0.5 * (2**attempt))
                continue
            raise


def send_slack_webhook(url: str, text: str, timeout_s: float = 15.0) -> None:
    _post_json(url, {"text": text}, timeout_s=timeout_s)


def send_teams_webhook(url: str, text: str, timeout_s: float = 15.0) -> None:
    # Incoming webhook connector accepts a simple body with "text" in many tenants.
    _post_json(url, {"text": text}, timeout_s=timeout_s)


def send_generic_webhook(url: str, text: str, timeout_s: float = 15.0) -> None:
    _post_json(url, {"text": text}, timeout_s=timeout_s)


def send_telegram(
    bot_token: str, chat_id: str, text: str, timeout_s: float = 15.0
) -> None:
    api = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    _post_form(api, {"chat_id": chat_id, "text": text}, timeout_s=timeout_s)


def send_to_first_configured_operator_channel(
    notifications_cfg: dict[str, Any],
    text: str,
    *,
    timeout_s: float = 15.0,
) -> tuple[str | None, bool, str | None]:
    """
    Send `text` using the first configured operator channel (Slack → Teams → Telegram → generic).

    Returns (channel_or_none, success, error_message).
    """
    op = notifications_cfg.get("operator") or {}
    if not isinstance(op, dict):
        op = {}

    slack = (op.get("slack_webhook_url") or "").strip()
    if slack:
        try:
            send_slack_webhook(slack, text, timeout_s=timeout_s)
            return "slack", True, None
        except (urllib.error.URLError, OSError, ValueError) as e:
            return "slack", False, str(e)

    teams = (op.get("teams_webhook_url") or "").strip()
    if teams:
        try:
            send_teams_webhook(teams, text, timeout_s=timeout_s)
            return "teams", True, None
        except (urllib.error.URLError, OSError, ValueError) as e:
            return "teams", False, str(e)

    token = (op.get("telegram_bot_token") or "").strip()
    chat = (op.get("telegram_chat_id") or "").strip()
    if token and chat:
        try:
            send_telegram(token, chat, text, timeout_s=timeout_s)
            return "telegram", True, None
        except (urllib.error.URLError, OSError, ValueError) as e:
            return "telegram", False, str(e)

    generic = (op.get("generic_webhook_url") or "").strip()
    if generic:
        try:
            send_generic_webhook(generic, text, timeout_s=timeout_s)
            return "generic", True, None
        except (urllib.error.URLError, OSError, ValueError) as e:
            return "generic", False, str(e)

    return None, False, "no operator webhook configured"


def build_scan_complete_message(
    summary: dict[str, Any],
    *,
    public_base_url: str | None = None,
) -> str:
    """Format a short pt-BR operator brief (counts + how to fetch report)."""
    sid = summary.get("session_id") or "?"
    total = int(summary.get("total_findings") or 0)
    high = int(summary.get("high") or 0)
    medium = int(summary.get("medium") or 0)
    low = int(summary.get("low") or 0)
    dob = int(summary.get("dob_possible_minor") or 0)
    failures = int(summary.get("scan_failures") or 0)
    tenant = summary.get("tenant_name") or "—"
    tech = summary.get("technician_name") or "—"
    status = summary.get("status") or "completed"
    lines = [
        "Data Boar — scan concluído",
        f"Sessão: {sid}",
        f"Status: {status}",
        f"Achados (total): {total} — HIGH: {high}, MEDIUM: {medium}, LOW: {low}",
        f"Possível menor (DOB_POSSIBLE_MINOR): {dob}",
        f"Falhas de target: {failures}",
        f"Inquilino: {tenant} | Técnico: {tech}",
        "Relatório Excel: página Reports no dashboard ou GET /report (último) ou GET /reports/{session_id}.",
        f"Heatmap: GET /heatmap/{sid}",
    ]
    base = (public_base_url or "").strip().rstrip("/")
    if base:
        lines.append(f"Base URL (se configurada): {base}")
    return "\n".join(lines)


def should_send_scan_complete_notification(
    config: dict[str, Any],
    summary: dict[str, Any],
) -> bool:
    """Return True if notifications are enabled and filters allow sending."""
    n = config.get("notifications") or {}
    if not isinstance(n, dict):
        return False
    if not bool(n.get("enabled", False)):
        return False
    is_err = (summary.get("status") or "") == "completed_errors"
    notify_fail = bool(n.get("notify_on_failure", True))
    # Worker-level failures: only when explicitly allowed (default on).
    if is_err:
        return notify_fail

    on_complete = bool(n.get("on_scan_complete", True))
    if not on_complete:
        return False
    if bool(n.get("notify_only_if_high_or_critical", False)):
        high = int(summary.get("high") or 0)
        dob = int(summary.get("dob_possible_minor") or 0)
        if high < 1 and dob < 1:
            return False
    return True


def notify_scan_complete_sync(
    config: dict[str, Any],
    db_manager: Any,
    session_id: str,
) -> None:
    """
    If configured, send one operator notification with session summary.

    Call after the session is finished and (for CLI) after report generation if desired.
    Does not raise on webhook errors; logs warnings.
    """
    summary = db_manager.get_session_scan_summary_for_notification(session_id)
    if not should_send_scan_complete_notification(config, summary):
        return
    n = config.get("notifications") or {}
    public_base = None
    if isinstance(n, dict):
        public_base = (n.get("public_base_url") or "").strip() or None
    text = build_scan_complete_message(summary, public_base_url=public_base)
    channel, ok, err = send_to_first_configured_operator_channel(n, text)
    if ok:
        _LOGGER.info(
            "Notification sent (scan complete): session=%s channel=%s",
            session_id,
            channel,
        )
    else:
        _LOGGER.warning(
            "Notification failed (scan complete): session=%s channel=%s err=%s",
            session_id,
            channel,
            err,
        )


def notify_scan_complete_background(
    config: dict[str, Any],
    db_manager: Any,
    session_id: str,
) -> None:
    """Fire-and-forget scan-complete notification (does not block CLI/API)."""

    def _run() -> None:
        try:
            notify_scan_complete_sync(config, db_manager, session_id)
        except Exception as e:
            _LOGGER.warning(
                "notify_scan_complete_background failed: session=%s err=%s",
                session_id,
                e,
            )

    threading.Thread(target=_run, daemon=True).start()


def send_manual_operator_message(
    config: dict[str, Any],
    text: str,
    *,
    timeout_s: float = 15.0,
) -> tuple[str | None, bool, str | None]:
    """
    Part A (off-band): send a free-form message if notifications.enabled is true
    and an operator channel is configured.
    """
    n = config.get("notifications") or {}
    if not isinstance(n, dict) or not bool(n.get("enabled", False)):
        return None, False, "notifications.enabled is false"
    return send_to_first_configured_operator_channel(n, text, timeout_s=timeout_s)
