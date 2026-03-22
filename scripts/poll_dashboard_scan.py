#!/usr/bin/env python3
"""
POST ``/scan`` on a Data Boar web dashboard, then poll ``/status`` until idle.

Operator / homelab helper — not used by CI. For a scan on another host, set the
base URL via environment **``DATA_BOAR_BASE``** or **``--base``** (e.g.
``http://127.0.0.1:8088``). Do **not** commit real lab hostnames or LAN URLs in
this repo; see root **``AGENTS.md``** and **``docs/PRIVATE_OPERATOR_NOTES.md``**.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:8088"


def get_json(base: str, path: str) -> dict:
    req = urllib.request.Request(f"{base.rstrip('/')}{path}", method="GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def post_json(base: str, path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{base.rstrip('/')}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument(
        "--base",
        default=os.environ.get("DATA_BOAR_BASE", DEFAULT_BASE).rstrip("/"),
        help=f"Dashboard root URL (default: env DATA_BOAR_BASE or {DEFAULT_BASE})",
    )
    args = p.parse_args(argv)
    base = args.base.rstrip("/")

    print("POST /scan ...")
    start = post_json(base, "/scan", {})
    print(json.dumps(start, indent=2))
    sid = start.get("session_id", "")
    for i in range(120):
        time.sleep(10)
        st = get_json(base, "/status")
        print(
            f"[{i}] running={st.get('running')} findings={st.get('findings_count')} "
            f"session={st.get('current_session_id')!r}"
        )
        if not st.get("running"):
            print("idle")
            print(json.dumps(get_json(base, "/status"), indent=2))
            if sid:
                print(f"\nDownload report: curl -sOJ {base}/reports/{sid}")
            return 0
    print("timeout 20min still running")
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.URLError as e:
        print("URLError:", e, file=sys.stderr)
        raise SystemExit(2) from e
