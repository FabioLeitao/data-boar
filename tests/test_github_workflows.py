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
    assert wr.get("workflows") == ["CI"]
    assert "notify" in (data.get("jobs") or {})
