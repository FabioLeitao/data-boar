"""Unit tests for ``scripts/ops_notify.py`` — no real network.

Covers the hardening contract documented in the script docstring:

* Env var precedence (``SLACK_WEBHOOK_DATA_BOAR_OPS`` > ``SLACK_WEBHOOK_URL``).
* Missing webhook returns exit code 3 with a clear MISSING_WEBHOOK marker.
* Bad ``--timeout`` is rejected with exit code 2.
* ``--dry-run`` does **not** touch the network.
* Successful POST returns exit code 0 and uses an explicit timeout.
* Permanent 4xx errors are not retried.
* Transient 5xx errors are retried up to the bounded ceiling.
* Webhook URL is **never** included in stderr / error output.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest
import requests

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "ops_notify.py"


def _load_module():
    """Import ``scripts/ops_notify.py`` as a module without polluting sys.path."""
    spec = importlib.util.spec_from_file_location("ops_notify", _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def ops_notify(monkeypatch):
    """Reload the script as a module with a clean env (no Slack vars by default)."""
    monkeypatch.delenv("SLACK_WEBHOOK_DATA_BOAR_OPS", raising=False)
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    module = _load_module()
    yield module
    # Best-effort: drop the dynamically loaded module from sys.modules so each
    # test starts clean.
    sys.modules.pop("ops_notify", None)


class _FakeResponse:
    def __init__(self, status_code: int = 200) -> None:
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if 400 <= self.status_code < 600:
            err = requests.HTTPError(f"HTTP {self.status_code}")
            err.response = self  # type: ignore[assignment]
            raise err


def _make_post_recorder(*responses: _FakeResponse | Exception):
    """Return a fake ``requests.post`` that yields ``responses`` in order.

    Each call records ``(url, kwargs)`` so tests can assert ``timeout`` is set.
    """
    calls: list[tuple[str, dict[str, Any]]] = []
    queue = list(responses)

    def fake_post(url: str, **kwargs: Any) -> _FakeResponse:
        calls.append((url, kwargs))
        if not queue:
            return _FakeResponse(200)
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    return fake_post, calls


def test_env_precedence_prefers_ops_var(ops_notify, monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_DATA_BOAR_OPS", "https://hooks.example/ops")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.example/general")
    url, name = ops_notify._resolve_webhook_url()
    assert url == "https://hooks.example/ops"
    assert name == "SLACK_WEBHOOK_DATA_BOAR_OPS"


def test_env_precedence_falls_back_to_generic(ops_notify, monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.example/general")
    url, name = ops_notify._resolve_webhook_url()
    assert url == "https://hooks.example/general"
    assert name == "SLACK_WEBHOOK_URL"


def test_env_precedence_ignores_blank(ops_notify, monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_DATA_BOAR_OPS", "   ")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.example/general")
    url, name = ops_notify._resolve_webhook_url()
    assert url == "https://hooks.example/general"
    assert name == "SLACK_WEBHOOK_URL"


def test_missing_webhook_exits_with_marker(ops_notify, capsys):
    rc = ops_notify.main(["hello"])
    captured = capsys.readouterr()
    assert rc == 3
    assert "MISSING_WEBHOOK" in captured.err


def test_invalid_timeout_rejected(ops_notify, monkeypatch, capsys):
    monkeypatch.setenv("SLACK_WEBHOOK_DATA_BOAR_OPS", "https://hooks.example/ops")
    rc = ops_notify.main(["--timeout", "0", "hello"])
    captured = capsys.readouterr()
    assert rc == 2
    assert "timeout" in captured.err.lower()


def test_dry_run_does_not_post(ops_notify, monkeypatch, capsys):
    monkeypatch.setenv("SLACK_WEBHOOK_DATA_BOAR_OPS", "https://hooks.example/ops")

    def explode(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("dry-run must not POST")

    monkeypatch.setattr(ops_notify.requests, "post", explode)
    rc = ops_notify.main(["--dry-run", "hello"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "dry-run OK" in captured.err
    assert "https://hooks.example/ops" not in captured.err


def test_successful_post_uses_explicit_timeout(ops_notify, monkeypatch, capsys):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.example/general")
    fake_post, calls = _make_post_recorder(_FakeResponse(200))
    monkeypatch.setattr(ops_notify.requests, "post", fake_post)

    rc = ops_notify.main(["--timeout", "5", "ship-it"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "sent" in captured.err
    assert len(calls) == 1
    _, kwargs = calls[0]
    assert kwargs.get("timeout") == 5
    assert "text" in (kwargs.get("json") or {})
    assert "ship-it" in kwargs["json"]["text"]
    # URL must never appear in stderr.
    assert "https://hooks.example/general" not in captured.err


def test_permanent_4xx_is_not_retried(ops_notify, monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.example/general")
    fake_post, calls = _make_post_recorder(_FakeResponse(404), _FakeResponse(200))
    monkeypatch.setattr(ops_notify.requests, "post", fake_post)
    monkeypatch.setattr(ops_notify.time, "sleep", lambda *_a, **_k: None)

    rc = ops_notify.main(["hello"])
    assert rc == 1
    assert len(calls) == 1


def test_transient_5xx_retries_up_to_ceiling(ops_notify, monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.example/general")
    fake_post, calls = _make_post_recorder(
        _FakeResponse(503), _FakeResponse(503), _FakeResponse(200)
    )
    monkeypatch.setattr(ops_notify.requests, "post", fake_post)
    monkeypatch.setattr(ops_notify.time, "sleep", lambda *_a, **_k: None)

    rc = ops_notify.main(["hello"])
    assert rc == 0
    assert len(calls) == 3


def test_timeout_exception_is_retried_then_fails(ops_notify, monkeypatch, capsys):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.example/general")
    fake_post, calls = _make_post_recorder(
        requests.Timeout("slow"),
        requests.Timeout("slow"),
        requests.Timeout("slow"),
    )
    monkeypatch.setattr(ops_notify.requests, "post", fake_post)
    monkeypatch.setattr(ops_notify.time, "sleep", lambda *_a, **_k: None)

    rc = ops_notify.main(["hello"])
    captured = capsys.readouterr()
    assert rc == 1
    assert len(calls) == 3
    assert "FAILED" in captured.err
    # URL must never appear in stderr.
    assert "https://hooks.example/general" not in captured.err
