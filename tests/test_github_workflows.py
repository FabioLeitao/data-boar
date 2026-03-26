"""Ensure operator Slack workflow files exist and parse as valid YAML.

Integration (real Slack POST) is not run in pytest; see docs/ops/OPERATOR_NOTIFICATION_CHANNELS.md §4.1.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _load_workflow(name: str) -> dict:
    path = WORKFLOWS / name
    assert path.is_file(), f"missing workflow file: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{name} must parse to a mapping"
    return data


def test_slack_operator_ping_workflow_present_and_valid() -> None:
    data = _load_workflow("slack-operator-ping.yml")
    assert data.get("name")
    assert "workflow_dispatch" in (data.get("on") or {})
    assert "ping" in (data.get("jobs") or {})


def test_slack_ci_failure_notify_workflow_present_and_valid() -> None:
    data = _load_workflow("slack-ci-failure-notify.yml")
    assert data.get("name")
    on = data.get("on") or {}
    assert "workflow_run" in on
    wr = on["workflow_run"]
    assert isinstance(wr, dict)
    assert wr.get("workflows") == ["CI", "Semgrep"]
    assert "notify" in (data.get("jobs") or {})


def test_semgrep_workflow_present_and_valid() -> None:
    data = _load_workflow("semgrep.yml")
    assert data.get("name") == "Semgrep"
    on = data.get("on") or {}
    assert "push" in on
    assert "pull_request" in on
    jobs = data.get("jobs") or {}
    assert "semgrep" in jobs
    job = jobs["semgrep"]
    assert job.get("runs-on") == "ubuntu-latest"
    container = job.get("container") or {}
    assert "semgrep" in str(container.get("image", "")).lower()


def _ci_step_run_texts(job: dict) -> list[str]:
    """Collect shell `run:` strings from a workflow job (scalar or folded YAML)."""
    out: list[str] = []
    for step in job.get("steps") or []:
        if not isinstance(step, dict):
            continue
        run = step.get("run")
        if isinstance(run, str):
            out.append(run)
    return out


def test_ci_lint_job_runs_pre_commit_all_files() -> None:
    """Regression guard: lint job must run pre-commit so CI matches local hook bundle (incl. Ruff, plans-stats)."""
    data = _load_workflow("ci.yml")
    assert data.get("name") == "CI"
    jobs = data.get("jobs") or {}
    lint = jobs.get("lint")
    assert isinstance(lint, dict), "ci.yml must define a lint job"
    assert "pre-commit" in str(lint.get("name", "")).lower(), (
        "lint job name should mention pre-commit"
    )
    runs = "\n".join(_ci_step_run_texts(lint))
    assert "pre-commit run --all-files" in runs
