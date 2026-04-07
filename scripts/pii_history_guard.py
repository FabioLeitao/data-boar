"""
History-focused PII anti-recurrence guard.

Default mode scans added lines in `origin/main..HEAD` diffs to block new
sensitive patterns before commit/PR.

Optional `--full-history` scans added lines across full git history.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCAN_RANGE = "origin/main..HEAD"

FORBIDDEN_LINE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "Windows absolute user path (non-placeholder)",
        re.compile(
            r"(?i)\bc:\\users\\"
            r"(?!<username>|<you>|user(?:name)?\b|public\b|default\b|all users\b|\.\.\.)"
            r"[a-z0-9._-]+\\"
        ),
    ),
    (
        "Linux absolute /home path (non-placeholder)",
        re.compile(
            r"(?i)(?<!\w)/home/"
            r"(?!user(?:/|$)|you(?:/|$)|<user>(?:/|$)|replace_user(?:/|$)|\{\{)"
            r"[a-z0-9._-]+/"
        ),
    ),
    (
        "LinkedIn profile URL (explicit personal slug)",
        re.compile(
            r"(?i)https?://(?:www\.)?linkedin\.com/in/"
            r"(?!example\b|<|\.{3}|replaced|redacted|\$|\{)[a-z0-9_-]+/?"
        ),
    ),
    (
        "Family relationship phrase (sensitive context)",
        re.compile(
            r"(?i)\b(my\s+wif[e]|my\s+sister(?:'s|s)\s+husband|esposa|cunhad[oa])\b"
        ),
    ),
    (
        "SSH URL with embedded user",
        re.compile(r"(?i)\bssh://[a-z0-9._-]+@"),
    ),
)

_HISTORY_GUARD_EXEMPT_PATHS = {"scripts/pii_history_guard.py"}


def _git(args: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc


def _resolve_scan_range(full_history: bool) -> str:
    if full_history:
        return "--all"
    origin_main = _git(["rev-parse", "--verify", "origin/main"])
    if origin_main.returncode == 0:
        return DEFAULT_SCAN_RANGE
    return "HEAD"


def _extract_added_lines(patch_text: str) -> list[str]:
    lines: list[str] = []
    current_path = ""
    for raw in patch_text.splitlines():
        if raw.startswith("+++ b/"):
            current_path = raw.removeprefix("+++ b/")
            continue
        if raw.startswith("+++ "):
            continue
        if raw.startswith("+"):
            if current_path in _HISTORY_GUARD_EXEMPT_PATHS:
                continue
            lines.append(raw[1:])
    return lines


def _collect_lines_to_scan(scan_range: str) -> list[str]:
    if scan_range == "--all":
        proc = _git(["log", "--all", "-p", "--unified=0", "--no-color", "--", "."])
    else:
        proc = _git(["diff", "--unified=0", "--no-color", scan_range, "--", "."])
    if proc.returncode != 0:
        raise RuntimeError(f"git patch scan failed: {proc.stderr.strip()}")
    return _extract_added_lines(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="PII history anti-recurrence guard")
    parser.add_argument(
        "--full-history",
        action="store_true",
        help="scan complete git history instead of origin/main..HEAD range",
    )
    args = parser.parse_args()

    if not (REPO_ROOT / ".git").exists():
        print("pii_history_guard: not a git repository; skipping.")
        return 0

    scan_range = _resolve_scan_range(args.full_history)
    lines = _collect_lines_to_scan(scan_range)
    violations: list[str] = []
    for idx, line in enumerate(lines, start=1):
        for label, pattern in FORBIDDEN_LINE_PATTERNS:
            if pattern.search(line):
                snippet = line.strip()
                if len(snippet) > 180:
                    snippet = snippet[:177] + "..."
                violations.append(f"{label} :: line#{idx} :: {snippet}")

    if violations:
        scope = "full history" if args.full_history else "origin/main..HEAD"
        print("PII history guard failed. Found forbidden patterns in git history:")
        print(f"  scope: {scope}")
        for violation in violations[:20]:
            print(f"  - {violation}")
        if len(violations) > 20:
            print(f"  ... {len(violations) - 20} more")
        print(
            "Remediate before commit/PR (filter-repo if needed). "
            "Do not push sensitive history."
        )
        return 1

    scope = "full history" if args.full_history else DEFAULT_SCAN_RANGE
    print(f"PII history guard: OK (no forbidden literals in {scope}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
