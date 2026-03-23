"""Tests for utils/notify.py (webhook POST; no real network)."""

from __future__ import annotations

import json
import urllib.error

from utils.notify import (
    build_scan_complete_message,
    send_slack_webhook,
    send_to_first_configured_operator_channel,
    should_send_scan_complete_notification,
)


def test_build_scan_complete_message_includes_session_and_counts():
    text = build_scan_complete_message(
        {
            "session_id": "sess_abc",
            "status": "completed",
            "high": 1,
            "medium": 2,
            "low": 3,
            "total_findings": 6,
            "dob_possible_minor": 0,
            "scan_failures": 0,
            "tenant_name": "T1",
            "technician_name": None,
        },
        public_base_url="https://example.test:8088",
    )
    assert "sess_abc" in text
    assert "HIGH: 1" in text
    assert "https://example.test:8088" in text


def test_should_send_respects_enabled_and_filters():
    cfg = {"notifications": {"enabled": False, "on_scan_complete": True}}
    summary = {"status": "completed", "high": 5, "dob_possible_minor": 0}
    assert should_send_scan_complete_notification(cfg, summary) is False

    cfg2 = {
        "notifications": {
            "enabled": True,
            "on_scan_complete": True,
            "notify_only_if_high_or_critical": True,
        }
    }
    assert (
        should_send_scan_complete_notification(
            cfg2, {"status": "completed", "high": 0, "dob_possible_minor": 0}
        )
        is False
    )
    assert (
        should_send_scan_complete_notification(
            cfg2, {"status": "completed", "high": 1, "dob_possible_minor": 0}
        )
        is True
    )


def test_should_send_completed_errors():
    cfg = {
        "notifications": {
            "enabled": True,
            "on_scan_complete": False,
            "notify_on_failure": True,
        }
    }
    assert (
        should_send_scan_complete_notification(
            cfg, {"status": "completed_errors", "high": 0, "dob_possible_minor": 0}
        )
        is True
    )
    cfg["notifications"]["notify_on_failure"] = False
    assert (
        should_send_scan_complete_notification(
            cfg, {"status": "completed_errors", "high": 0, "dob_possible_minor": 0}
        )
        is False
    )


def test_send_slack_uses_json_post(monkeypatch):
    captured: dict[str, bytes] = {}

    def fake_urlopen(req, timeout=None):
        captured["body"] = req.data

        class R:
            def read(self):
                return b"ok"

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        return R()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    n = {
        "operator": {
            "slack_webhook_url": "https://hooks.slack.example/services/XXX",
        }
    }
    ch, ok, err = send_to_first_configured_operator_channel(n, "hello")
    assert ok is True
    assert ch == "slack"
    assert captured["body"] is not None
    payload = json.loads(captured["body"].decode())
    assert payload.get("text") == "hello"


def test_send_no_channel_returns_error():
    ch, ok, err = send_to_first_configured_operator_channel({}, "x")
    assert ok is False
    assert ch is None
    assert "no operator" in (err or "").lower()


def test_send_slack_retries_once_on_502(monkeypatch):
    calls = {"n": 0}

    def fake_urlopen(req, timeout=None):
        calls["n"] += 1
        if calls["n"] < 2:
            raise urllib.error.HTTPError("http://hook", 502, "Bad", {}, None)

        class R:
            def read(self):
                return b"ok"

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        return R()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("utils.notify.time.sleep", lambda *_a, **_k: None)
    send_slack_webhook("https://hooks.example/hook", "hi")
    assert calls["n"] == 2
