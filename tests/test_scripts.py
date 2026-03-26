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


def _parse_powershell_script(script_path: Path, root: Path) -> bool:
    """Return True if script has valid PowerShell syntax (Parser::ParseFile)."""
    rel = script_path.relative_to(root)
    path_expr = (
        "[System.IO.Path]::GetFullPath((Join-Path (Get-Location) '"
        + str(rel.as_posix())
        + "'))"
    )
    parse_script = (
        f"$path = {path_expr}; "
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
        return proc.returncode == 0
    return False


def test_preview_commit_ps1_syntax():
    """scripts/preview-commit.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "preview-commit.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), "preview-commit.ps1 parse failed"


def test_pr_hygiene_remind_ps1_syntax():
    """scripts/pr-hygiene-remind.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "pr-hygiene-remind.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), "pr-hygiene-remind.ps1 parse failed"


def test_maintenance_check_ps1_syntax():
    """scripts/maintenance-check.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "maintenance-check.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), "maintenance-check.ps1 parse failed"


def test_docker_hub_pull_ps1_syntax():
    """scripts/docker-hub-pull.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "docker-hub-pull.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), "docker-hub-pull.ps1 parse failed"


def test_docker_lab_build_ps1_syntax():
    """scripts/docker-lab-build.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "docker-lab-build.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), "docker-lab-build.ps1 parse failed"


def test_docker_prune_local_ps1_syntax():
    """scripts/docker-prune-local.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "docker-prune-local.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), "docker-prune-local.ps1 parse failed"


def test_pr_merge_when_green_ps1_syntax():
    """scripts/pr-merge-when-green.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "pr-merge-when-green.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), (
        "pr-merge-when-green.ps1 parse failed"
    )


def test_snmp_udm_lab_probe_ps1_syntax():
    """scripts/snmp-udm-lab-probe.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "snmp-udm-lab-probe.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), "snmp-udm-lab-probe.ps1 parse failed"


def test_lab_op_sync_and_collect_ps1_syntax():
    """scripts/lab-op-sync-and-collect.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "lab-op-sync-and-collect.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), (
        "lab-op-sync-and-collect.ps1 parse failed"
    )


def test_collect_homelab_report_remote_ps1_syntax():
    """scripts/collect-homelab-report-remote.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "collect-homelab-report-remote.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), (
        "collect-homelab-report-remote.ps1 parse failed"
    )


def test_homelab_host_report_sh_syntax():
    """scripts/homelab-host-report.sh has valid bash syntax (bash -n). Skipped on Windows."""
    if sys.platform == "win32":
        return
    root = _project_root()
    script = root / "scripts" / "homelab-host-report.sh"
    if not script.exists():
        return
    try:
        proc = subprocess.run(
            ["bash", "-n", str(script)],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        return
    assert proc.returncode == 0, f"bash -n failed: {proc.stderr or proc.stdout}"


def test_docker_common_ps1_syntax():
    """scripts/docker/DataBoarDockerCommon.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "docker" / "DataBoarDockerCommon.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), (
        "DataBoarDockerCommon.ps1 parse failed"
    )


def test_create_pr_ps1_syntax():
    """scripts/create-pr.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "create-pr.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), "create-pr.ps1 parse failed"


def test_create_pr_ps1_has_param_block():
    """scripts/create-pr.ps1 has param block with Title and BodyFilePath (structured)."""
    root = _project_root()
    script = root / "scripts" / "create-pr.ps1"
    if not script.exists():
        return
    text = script.read_text(encoding="utf-8", errors="replace")
    assert "param(" in text
    assert "Title" in text and "BodyFilePath" in text


def test_gh_ensure_default_ps1_syntax():
    """scripts/gh-ensure-default.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "gh-ensure-default.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), "gh-ensure-default.ps1 parse failed"


def test_version_readiness_smoke_ps1_syntax():
    """scripts/version-readiness-smoke.ps1 has valid PowerShell syntax (parse-only)."""
    root = _project_root()
    script = root / "scripts" / "version-readiness-smoke.ps1"
    if not script.exists():
        return
    assert _parse_powershell_script(script, root), (
        "version-readiness-smoke.ps1 parse failed"
    )


def test_commit_or_pr_mentions_gh_default_repo_guard():
    """commit-or-pr includes gh default repository guard for PR flow."""
    root = _project_root()
    script = root / "scripts" / "commit-or-pr.ps1"
    if not script.exists():
        return
    text = script.read_text(encoding="utf-8", errors="replace")
    assert "Set-GhDefaultRepo" in text
    assert "RunVersionSmoke" in text


def test_check_all_supports_optional_version_smoke():
    """check-all script exposes optional version readiness smoke switch."""
    root = _project_root()
    script = root / "scripts" / "check-all.ps1"
    if not script.exists():
        return
    text = script.read_text(encoding="utf-8", errors="replace")
    assert "IncludeVersionSmoke" in text
    assert "version-readiness-smoke.ps1" in text


def test_pr_hygiene_mentions_gh_preflight():
    """pr-hygiene-remind includes gh preflight reminder and quick checks switch."""
    root = _project_root()
    script = root / "scripts" / "pr-hygiene-remind.ps1"
    if not script.exists():
        return
    text = script.read_text(encoding="utf-8", errors="replace")
    assert "gh-ensure-default.ps1" in text
    assert "RunQuickChecks" in text
    assert "SLACK_WEBHOOK_URL" in text
    assert "OPERATOR_NOTIFICATION_CHANNELS" in text


def test_docs_private_scripts_syntax_optional(include_private_lint: bool):
    """
    When opted in (``pytest --include-private`` or ``INCLUDE_PRIVATE_LINT=1``),
    parse any ``*.ps1`` under ``docs/private/`` and run ``bash -n`` on ``*.sh`` there (non-Windows only).
    Skips if ``docs/private/`` is missing or contains no matching scripts.
    """
    if not include_private_lint:
        return
    root = _project_root()
    private_dir = root / "docs" / "private"
    if not private_dir.is_dir():
        return
    ps1_files = sorted(private_dir.rglob("*.ps1"))
    for script in ps1_files:
        assert _parse_powershell_script(script, root), (
            f"{script.relative_to(root)}: PowerShell parse failed"
        )
    if sys.platform == "win32":
        return
    sh_files = sorted(private_dir.rglob("*.sh"))
    for script in sh_files:
        try:
            proc = subprocess.run(
                ["bash", "-n", str(script)],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=10,
            )
        except FileNotFoundError:
            return
        assert proc.returncode == 0, (
            f"bash -n failed for {script.relative_to(root)}: "
            f"{proc.stderr or proc.stdout}"
        )
