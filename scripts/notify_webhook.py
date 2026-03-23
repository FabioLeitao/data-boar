#!/usr/bin/env python3
"""
Post a manual operator message using the configured notifications block (Part A: off-band).

Requires notifications.enabled: true and at least one operator channel in config.
Usage (from repo root):

  uv run python scripts/notify_webhook.py "Build green on main"
  echo "Release cut" | uv run python scripts/notify_webhook.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from config.loader import load_config  # noqa: E402
from utils.notify import send_manual_operator_message  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a one-off message via configured operator webhook(s)."
    )
    parser.add_argument(
        "message",
        nargs="?",
        default="",
        help="Message text (default: read stdin)",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML/JSON config",
    )
    args = parser.parse_args()
    text = (args.message or "").strip()
    if not text:
        text = sys.stdin.read()
    text = text.strip()
    if not text:
        print("No message text.", file=sys.stderr)
        sys.exit(2)
    try:
        cfg = load_config(args.config)
    except Exception as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)
    _ch, ok, err = send_manual_operator_message(cfg, text)
    if ok:
        print("Notification sent.")
        sys.exit(0)
    print(f"Not sent: {err}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
