#!/usr/bin/env python3
"""
Hardened Slack telemetry CLI for Data Boar operations.

Posts a short message to the operator Slack workspace via an Incoming Webhook URL
read from an environment variable. Designed for ad-hoc operator pings, lab smoke
heartbeats, and CI-side telemetry (e.g. completão runners) where a full
``scripts/notify_webhook.py`` round-trip (config + SQLite audit) is overkill.

Why a separate script (and not ``scripts/notify_webhook.py``)?

* ``notify_webhook.py`` requires ``config.yaml`` with ``notifications.enabled: true``
  and at least one configured operator channel. That is the right path for the
  product (scan-complete notifications, audit log).
* ``ops_notify.py`` is the right path for **operational telemetry** — short
  heartbeats from scripts, CI jobs, and lab orchestration where there is no
  YAML config in scope and only an environment variable is available.

Environment variables (precedence: first defined, non-empty wins)

* ``SLACK_WEBHOOK_DATA_BOAR_OPS`` — preferred for ops telemetry. Lets the
  operator route ops pings to a dedicated ``#data-boar-ops`` channel without
  touching the general ``SLACK_WEBHOOK_URL`` used by GitHub Actions.
* ``SLACK_WEBHOOK_URL`` — fallback. Same secret as
  ``.github/workflows/slack-operator-ping.yml`` and friends.

Hardening (vs the naïve ``requests.post(webhook_url, json=payload)``):

* Explicit ``timeout`` on the HTTP call (mitigates Bandit B113 and avoids
  hanging on a slow webhook).
* ``raise_for_status()`` plus a small bounded retry loop on transient errors
  (5xx, connection/read timeouts) — same backoff philosophy as
  ``utils/notify.py`` (3 attempts, exponential, no ``time.sleep`` for SQL
  contention; sleeps only between webhook retries).
* Webhook URL is **never** printed: error paths only show the exception class
  and message, never the secret URL.
* Exit codes are explicit (``0`` ok, ``1`` send failed, ``2`` bad input, ``3``
  missing webhook), so CI / cron can branch on the result.
* ``--dry-run`` resolves the webhook env, validates input, and returns ``0``
  **without** posting — used by tests and operator smoke (does not depend on
  network availability or a live Slack workspace).

Usage (from repo root)::

    uv run python scripts/ops_notify.py "Heartbeat: completão runner started"
    echo "Lab smoke: HOST_A green" | uv run python scripts/ops_notify.py
    SLACK_WEBHOOK_DATA_BOAR_OPS=https://hooks.slack.example/T/B/X \
        uv run python scripts/ops_notify.py --dry-run "smoke check"
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Final

import requests

# Bounded retry policy. Mirrors utils.notify._WEBHOOK_MAX_ATTEMPTS so operator
# experience is consistent across the two notification entrypoints.
_MAX_ATTEMPTS: Final[int] = 3
_BACKOFF_SECONDS_BASE: Final[float] = 0.5
_DEFAULT_TIMEOUT_SECONDS: Final[float] = 10.0
_DEFAULT_PREFIX: Final[str] = "DATA BOAR TELEMETRY"

# Order matters: ops-specific env var wins over the generic one used by
# GitHub Actions, so an operator can split ops telemetry from PR/CI alerts.
_WEBHOOK_ENV_VARS: Final[tuple[str, ...]] = (
    "SLACK_WEBHOOK_DATA_BOAR_OPS",
    "SLACK_WEBHOOK_URL",
)


def _resolve_webhook_url() -> tuple[str | None, str | None]:
    """Return ``(url, env_var_name)`` for the first defined, non-empty env var.

    Returns ``(None, None)`` when none is set. The env var **name** is returned
    (never the URL) so callers can log which channel routing applied without
    leaking the secret.
    """
    for name in _WEBHOOK_ENV_VARS:
        raw = os.environ.get(name, "")
        value = raw.strip() if isinstance(raw, str) else ""
        if value:
            return value, name
    return None, None


def _read_message(args_message: str) -> str:
    """Resolve the message text from CLI argument, then stdin, then the default."""
    text = (args_message or "").strip()
    if text:
        return text
    if not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        if text:
            return text
    return "Heartbeat: Data Boar operational agent."


def _format_payload(message: str, prefix: str) -> dict[str, str]:
    """Format a Slack ``{"text": ...}`` payload.

    The Slack Incoming Webhook contract accepts a minimal JSON body with a
    ``text`` field; we keep the shape identical to ``utils.notify.send_slack_webhook``
    for cross-tool consistency.
    """
    safe_prefix = (prefix or _DEFAULT_PREFIX).strip() or _DEFAULT_PREFIX
    return {"text": f":boar: *{safe_prefix}* :boar:\n{message}"}


def _post_with_retry(
    url: str,
    payload: dict[str, str],
    *,
    timeout_s: float,
    max_attempts: int = _MAX_ATTEMPTS,
) -> tuple[bool, str | None]:
    """POST ``payload`` to ``url`` with bounded exponential backoff.

    Returns ``(ok, error_message)``. ``error_message`` never contains the
    webhook URL — only the exception class name and a short reason — so logs
    and Slack/GitHub transcripts cannot leak the secret.
    """
    last_error: str | None = None
    for attempt in range(max_attempts):
        try:
            response = requests.post(url, json=payload, timeout=timeout_s)
            response.raise_for_status()
            return True, None
        except requests.HTTPError as exc:
            status = getattr(exc.response, "status_code", None)
            last_error = f"HTTPError status={status}"
            # 4xx (other than 429) is permanent: bad payload, revoked webhook,
            # archived channel. Retrying would just duplicate the failure.
            if status is not None and status < 500 and status != 429:
                return False, last_error
        except requests.Timeout as exc:
            last_error = f"Timeout: {type(exc).__name__}"
        except requests.ConnectionError as exc:
            last_error = f"ConnectionError: {type(exc).__name__}"
        except requests.RequestException as exc:
            last_error = f"RequestException: {type(exc).__name__}"

        if attempt < max_attempts - 1:
            # Exponential backoff between webhook retries only. This is *not*
            # a SQL-contention sleep (anti-pattern called out in the SRE
            # protocol) — it is the standard webhook retry pacing.
            time.sleep(_BACKOFF_SECONDS_BASE * (2**attempt))

    return False, last_error or "unknown send error"


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ops_notify.py",
        description=(
            "Post a short telemetry message to the Data Boar operator Slack "
            "via an Incoming Webhook URL read from "
            "SLACK_WEBHOOK_DATA_BOAR_OPS (preferred) or SLACK_WEBHOOK_URL."
        ),
    )
    parser.add_argument(
        "message",
        nargs="?",
        default="",
        help=(
            "Message text. If omitted and stdin is piped, reads stdin. "
            "Defaults to a generic heartbeat string when both are empty."
        ),
    )
    parser.add_argument(
        "--prefix",
        default=_DEFAULT_PREFIX,
        help=f"Bold header line shown before the message (default: {_DEFAULT_PREFIX!r}).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=_DEFAULT_TIMEOUT_SECONDS,
        help=(
            "HTTP timeout in seconds for the webhook POST "
            f"(default: {_DEFAULT_TIMEOUT_SECONDS})."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate env + message and exit 0 without posting. Used by tests "
            "and operator smoke; never touches the network."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if args.timeout <= 0:
        print("ops_notify: --timeout must be positive seconds.", file=sys.stderr)
        return 2

    url, env_name = _resolve_webhook_url()
    message = _read_message(args.message)

    if url is None:
        print(
            "ops_notify: MISSING_WEBHOOK — set SLACK_WEBHOOK_DATA_BOAR_OPS "
            "(preferred) or SLACK_WEBHOOK_URL. Telemetry offline.",
            file=sys.stderr,
        )
        return 3

    if args.dry_run:
        # Never log the URL — only confirm which env routing applied.
        print(
            f"ops_notify: dry-run OK (env={env_name}, message_len={len(message)}).",
            file=sys.stderr,
        )
        return 0

    payload = _format_payload(message, args.prefix)
    ok, err = _post_with_retry(url, payload, timeout_s=args.timeout)
    if ok:
        print(f"ops_notify: sent (env={env_name}).", file=sys.stderr)
        return 0

    print(
        f"ops_notify: send FAILED after {_MAX_ATTEMPTS} attempts (env={env_name}): {err}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
