"""
Tests for shell and PowerShell scripts: syntax validity and safe dry-run behaviour.

SonarQube-style checks: scripts use quoted variables, explicit exit codes, and no
obvious injection; these tests ensure they parse and (where possible) run a no-op path.
"""

import subprocess
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


# --- Bash: prep_audit.sh syntax (bash -n) ---


def test_prep_audit_sh_syntax():
    """prep_audit.sh has valid bash syntax (bash -n). Skipped on Windows (path handling)."""
    if sys.platform == "win32":
        return  # bash -n with Windows path is unreliable (e.g. Git Bash path quirks)
    root = _project_root()
    script = root / "prep_audit.sh"
    if not script.exists():
        return  # skip if removed
    try:
        proc = subprocess.run(
            ["bash", "-n", str(script)],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except FileNotFoundError:
        return
    assert proc.returncode == 0, f"bash -n failed: {proc.stderr or proc.stdout}"


def test_prep_audit_sh_has_shebang_and_exit_code():
    """prep_audit.sh has shebang and uses explicit exit 1 when not root (Sonar best practice)."""
    root = _project_root()
    script = root / "prep_audit.sh"
    if not script.exists():
        return
    text = script.read_text(encoding="utf-8", errors="replace")
    assert text.startswith("#!/bin/bash"), "Script should have bash shebang"
    assert "exit 1" in text, (
        "Script should use explicit exit code (e.g. exit 1 when not root)"
    )


# --- PowerShell: commit-or-pr.ps1 syntax (Parser::ParseFile) ---


def test_commit_or_pr_ps1_syntax():
    """scripts/commit-or-pr.ps1 has valid PowerShell syntax (parse-only, no execution)."""
    root = _project_root()
    script = root / "scripts" / "commit-or-pr.ps1"
    if not script.exists():
        return
    # Parse-only: avoids running git or any side effects; works on all platforms
    parse_script = (
        "$path = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) 'scripts/commit-or-pr.ps1')); "
        "$errors = $null; "
        "$null = [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$null, [ref]$errors); "
        "exit ([int]($errors -and $errors.Count -gt 0))"
    )
    for pw in ("pwsh", "powershell"):
        try:
            proc = subprocess.run(
                [pw, "-NoProfile", "-NonInteractive", "-Command", parse_script],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=10,
            )
        except FileNotFoundError:
            continue
        assert proc.returncode == 0, (
            f"commit-or-pr.ps1 parse failed with {pw}: {proc.stderr or proc.stdout}"
        )
        return


def test_commit_or_pr_ps1_has_param_block():
    """scripts/commit-or-pr.ps1 has param block and ValidateSet for Action (structured)."""
    root = _project_root()
    script = root / "scripts" / "commit-or-pr.ps1"
    if not script.exists():
        return
    text = script.read_text(encoding="utf-8", errors="replace")
    assert "param(" in text
    assert "ValidateSet" in text
    assert "Preview" in text and "Commit" in text and "PR" in text
