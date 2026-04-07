"""
Guardrail: tracked files must not contain PII patterns that belong
only in docs/private/ (gitignored stacked private repo).

Scans every file in the Git index for known sensitive literal strings
and regex patterns.  An optional external patterns file
(docs/private/pii-patterns.txt, gitignored) extends the built-in list
without exposing the patterns publicly.

RCA: PII was accidentally committed in .cursor/rules/ and scripts/.
Detected and scrubbed via git filter-repo.  This guard prevents
recurrence.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

_BUILTIN_LITERALS: list[str] = [
    "ictsi_dossie",
    "ictsi_dossier",
    "caso trabalhista",
    "dossie juridico",
    "processo juridico",
    "INDICE_EVIDENCIAS",
    "SUMARIO_EXECUTIVO_DOSSIE",
    "RISCOS_E_PROTECOES_PARA_ESPOSA",
    "CARTA_DISCLOSURE_KUM_CHAI",
]

_BUILTIN_REGEXES: list[tuple[str, re.Pattern[str]]] = [
    ("CRM with digits (medical license)", re.compile(r"CRM-\d{4,}")),
]

_PRIVATE_PATTERNS_FILE = REPO_ROOT / "docs" / "private" / "pii-patterns.txt"

_ALLOWED_PATHS_PREFIXES = (
    "docs/private/",
    "docs/private.example/",
    ".cursor/private/",
    "tests/test_pii_guard.py",
)

_BINARY_EXTENSIONS = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".webp",
        ".svg",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".pyc",
        ".pyo",
        ".so",
        ".dll",
        ".exe",
        ".zip",
        ".gz",
        ".tar",
        ".bz2",
        ".xz",
        ".xlsx",
        ".xls",
        ".pdf",
        ".db",
        ".sqlite",
        ".sqlite3",
        ".lock",
        ".gpg",
    }
)


def _git_ls_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0 or not (REPO_ROOT / ".git").exists():
        pytest.skip("Not a git checkout or git ls-files failed.")
    raw = proc.stdout.split(b"\0")
    return [
        chunk.decode("utf-8", errors="replace").replace("\\", "/")
        for chunk in raw
        if chunk
    ]


def _load_private_patterns() -> list[str]:
    if not _PRIVATE_PATTERNS_FILE.is_file():
        return []
    return [
        line.strip()
        for line in _PRIVATE_PATTERNS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _is_allowed(path: str) -> bool:
    return any(path.startswith(pfx) for pfx in _ALLOWED_PATHS_PREFIXES)


def _is_binary(path: str) -> bool:
    return Path(path).suffix.lower() in _BINARY_EXTENSIONS


def test_tracked_files_contain_no_pii_patterns():
    """Fail CI if any tracked file contains a known PII pattern."""
    all_literals = list(_BUILTIN_LITERALS) + _load_private_patterns()
    tracked = _git_ls_files()
    violations: list[str] = []

    for fpath in tracked:
        if _is_allowed(fpath) or _is_binary(fpath):
            continue
        full = REPO_ROOT / fpath
        if not full.is_file():
            continue
        try:
            content = full.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        lower_content = content.lower()
        for lit in all_literals:
            if lit.lower() in lower_content:
                violations.append(f"  {fpath}: contains PII literal '{lit}'")

        for label, pattern in _BUILTIN_REGEXES:
            if pattern.search(content):
                violations.append(f"  {fpath}: matches PII regex '{label}'")

    assert not violations, (
        "PII guard failed -- move sensitive content to docs/private/ "
        "(gitignored stacked private repo):\n" + "\n".join(violations)
    )


def test_gitignore_covers_dossier_rule():
    """The old dossier rule file must stay gitignored."""
    gi = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8", errors="replace")
    assert ".cursor/rules/dossier-update-on-evidence.mdc" in gi, (
        ".gitignore must keep .cursor/rules/dossier-update-on-evidence.mdc ignored"
    )
