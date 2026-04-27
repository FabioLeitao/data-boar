"""
Bandit security-linter regression guard (Phase 3 of PLAN_BANDIT_SECURITY_LINTER.md).

After the doctrine-aligned `# nosec BXXX` triage of every previously-flagged low
finding, this test pins the contract:

    bandit -c pyproject.toml -r <product paths> -l    --->   exit 0, zero findings.

If a future change re-introduces a Bandit issue at any severity, this test
trips locally before CI does. The intent is the same as
`tests/test_pii_guard.py`: encode the lesson in the suite so regressions
cannot land silently.

Why -l (low+) and not -ll (medium+):

  - DEFENSIVE_SCANNING_MANIFESTO.md says the scanner is a guest in the
    customer environment; "low" findings (try/except/pass swallowing
    errors, subprocess on PATH binaries, hardcoded URL templates) are the
    exact noise patterns that hide regressions when left unjustified. The
    triage keeps every kept-as-is pattern paired with a `# nosec BXXX`
    plus an above-the-line comment explaining *why* the demotion is
    intentional - matching THE_ART_OF_THE_FALLBACK.md "diagnostic on
    fall" rule.

  - We deliberately do not import `bandit` as a Python module here; we
    invoke the same CLI string CI uses so the contract drifts only when
    the workflow YAML and the test agree. The test is skipped if the
    CLI is unavailable (e.g. minimal contributor checkout without
    `uv sync --group dev`).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Same scope as `.github/workflows/ci.yml` Bandit job and PLAN_BANDIT_SECURITY_LINTER.md.
_BANDIT_PATHS = [
    "api",
    "core",
    "config",
    "connectors",
    "database",
    "file_scan",
    "report",
    "main.py",
]


def _bandit_available() -> bool:
    return shutil.which("bandit") is not None or _bandit_via_module()


def _bandit_via_module() -> bool:
    try:
        import bandit  # noqa: F401

        return True
    except Exception:
        return False


@pytest.mark.skipif(not _bandit_available(), reason="bandit CLI/module not installed")
def test_bandit_low_severity_clean() -> None:
    """Bandit must report zero findings at low+ severity across product code."""
    cmd = [
        sys.executable,
        "-m",
        "bandit",
        "-c",
        "pyproject.toml",
        "-r",
        *_BANDIT_PATHS,
        "-f",
        "json",
        "-l",
    ]
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    payload = proc.stdout or ""
    # Bandit prepends a "Working... 100%" progress line to stdout even in JSON
    # mode; the actual JSON document starts at the first '{' on its own line.
    brace = payload.find("\n{")
    if brace != -1:
        payload = payload[brace + 1 :]
    payload = payload.strip()
    assert payload, "bandit produced no JSON output (stderr=%s)" % (
        proc.stderr or "<empty>"
    )
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:  # pragma: no cover - debugging aid
        pytest.fail(f"bandit JSON parse failed: {exc}\n{payload[:2000]}")

    results = data.get("results") or []
    if results:
        # Surface a compact, reviewable summary - same shape an operator would
        # want in a PR review when this guard trips.
        sample = "\n".join(
            f"  {r['test_id']:5s} {r['issue_severity']:7s} "
            f"{r['filename']}:{r['line_number']}: {r['issue_text'][:120]}"
            for r in results[:25]
        )
        more = "" if len(results) <= 25 else f"\n  ... and {len(results) - 25} more"
        pytest.fail(
            "Bandit reported "
            f"{len(results)} low+ severity finding(s):\n"
            f"{sample}{more}\n\n"
            "Triage required: either fix the code, or add `# nosec BXXX` on the "
            "exact `pass`/`continue`/call line plus a one-line comment above "
            "explaining *why*, anchored to docs/ops/inspirations/* doctrine. "
            "See PLAN_BANDIT_SECURITY_LINTER.md (Phase 3) and "
            "docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md."
        )
