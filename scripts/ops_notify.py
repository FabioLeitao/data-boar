#!/usr/bin/env python3
"""
Post a short telemetry line to Slack (#data-boar-ops) via Incoming Webhook.

Reads the webhook URL **only** from environment variables (never from argv or
tracked files). Resolution order:

1. ``SLACK_WEBHOOK_URL`` — same name as GitHub Actions and
   ``scripts/social-x-pace-remind.ps1`` (see ``docs/ops/OPERATOR_NOTIFICATION_CHANNELS.md``).
2. ``SLACK_WEBHOOK_DATA_BOAR_OPS`` — optional alternate for local tooling.

Usage::

  uv run python scripts/ops_notify.py "Custom message"
  uv run python scripts/ops_notify.py   # default heartbeat text
"""

from __future__ import annotations

import os
import sys
from typing import Final

import requests

_DEFAULT_MESSAGE: Final[str] = "Heartbeat: Agente Operacional."
_REQUEST_TIMEOUT_S: Final[float] = 15.0


def _resolve_webhook_url() -> str | None:
    primary = (os.environ.get("SLACK_WEBHOOK_URL") or "").strip()
    if primary:
        return primary
    legacy = (os.environ.get("SLACK_WEBHOOK_DATA_BOAR_OPS") or "").strip()
    if legacy:
        return legacy
    return None


def send_telemetry(message: str) -> int:
    """
    POST ``message`` to Slack. Returns 0 if skipped or sent OK, 1 on HTTP/transport error.
    """
    webhook_url = _resolve_webhook_url()
    if not webhook_url:
        print("MISSING_WEBHOOK: Telemetry offline.", file=sys.stderr)
        return 0

    payload = {"text": f"*DATA BOAR TELEMETRY*\n{message}"}
    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            timeout=_REQUEST_TIMEOUT_S,
        )
    except requests.RequestException as exc:
        print(f"SLACK_POST_FAILED: {exc}", file=sys.stderr)
        return 1

    if not resp.ok:
        snippet = (resp.text or "")[:200]
        print(
            f"SLACK_POST_FAILED: HTTP {resp.status_code} {snippet!r}",
            file=sys.stderr,
        )
        return 1

    return 0


def main() -> int:
    msg = sys.argv[1] if len(sys.argv) > 1 else _DEFAULT_MESSAGE
    return send_telemetry(msg)


if __name__ == "__main__":
    raise SystemExit(main())
