"""
Chaos / SRE safeguards for the REST connector.

These tests exercise the failure modes called out in
``docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`` and
``THE_ART_OF_THE_FALLBACK.md``:

- The detector receiving a multi-gigabyte response body (the "1 GB string"
  scenario) must be refused before it can fill memory.
- Adversarially nested or extremely wide JSON must not raise ``RecursionError``
  or pin a CPU walking millions of keys.
- Every demotion (refused body, depth/width truncation) must be observable —
  silent failure is the failure mode this manifesto exists to prevent.

The tests do **not** open real sockets and do **not** touch any database.
"""

from __future__ import annotations

import importlib.util
import json
from unittest.mock import MagicMock, patch

import pytest


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


# ---------------------------------------------------------------------------
# _flatten_sample: bounded against adversarial JSON shapes
# ---------------------------------------------------------------------------


class TestFlattenSampleDefensiveCaps:
    """JSON walk must never raise RecursionError or scan unbounded width."""

    def test_deep_nesting_does_not_recurse(self):
        from connectors.rest_connector import _flatten_sample

        # Build {"a": {"a": {"a": ... 5_000 levels deep ... }}}.
        depth = 5_000
        payload: dict = {}
        cur = payload
        for _ in range(depth):
            nxt: dict = {}
            cur["a"] = nxt
            cur = nxt
        cur["a"] = "leaf"

        rows = _flatten_sample(payload, max_len=500)

        # We expect at least one truncation row; we MUST NOT raise.
        truncations = [r for r in rows if r[1].startswith("max_depth=")]
        assert truncations, "deep payload should record a max_depth truncation"

    def test_wide_dict_is_bounded(self):
        from connectors.rest_connector import (
            _DEFAULT_FLATTEN_MAX_KEYS_PER_LEVEL,
            _flatten_sample,
        )

        wide = {f"k{i}": i for i in range(_DEFAULT_FLATTEN_MAX_KEYS_PER_LEVEL * 5)}
        rows = _flatten_sample(wide, max_len=500)

        scalar_rows = [r for r in rows if not r[1].startswith("max_keys_per_level=")]
        assert len(scalar_rows) <= _DEFAULT_FLATTEN_MAX_KEYS_PER_LEVEL
        assert any(r[1].startswith("max_keys_per_level=") for r in rows), (
            "wide payload should record a max_keys_per_level truncation"
        )

    def test_total_rows_is_bounded(self):
        from connectors.rest_connector import (
            _DEFAULT_FLATTEN_MAX_KEYS_PER_LEVEL,
            _DEFAULT_FLATTEN_MAX_TOTAL_ROWS,
            _flatten_sample,
        )

        # Force a payload that would otherwise emit >max_total_rows entries.
        # We use slightly-wider-than-cap dicts nested a few levels so the total
        # keeps growing past the row ceiling.
        levels = 6
        keys_per_level = _DEFAULT_FLATTEN_MAX_KEYS_PER_LEVEL
        payload: dict = {}
        cur = payload
        for level in range(levels):
            for i in range(keys_per_level):
                cur[f"k{level}_{i}"] = i
            child: dict = {}
            cur["next"] = child
            cur = child

        rows = _flatten_sample(payload, max_len=500)
        # Output must respect the global row ceiling and must surface a reason.
        assert len(rows) <= _DEFAULT_FLATTEN_MAX_TOTAL_ROWS + 5
        assert any(
            r[1].startswith("max_total_rows=") or r[1].startswith("max_keys_per_level=")
            for r in rows
        ), "oversize payload must record a truncation reason"

    def test_normal_payload_still_works(self):
        """Sanity: small payloads keep their original shape (no false truncation)."""
        from connectors.rest_connector import _flatten_sample

        rows = _flatten_sample(
            {"user": {"id": 7, "email": "x@y.co"}, "tags": ["a", "b"]},
            max_len=500,
        )
        keys = {r[0] for r in rows}
        assert "user.id" in keys
        assert "user.email" in keys
        # No truncation rows for a healthy payload.
        assert not any(r[1].startswith("max_") for r in rows)


# ---------------------------------------------------------------------------
# _resolve_max_response_bytes: env clamp
# ---------------------------------------------------------------------------


class TestResponseByteCapResolution:
    def test_default_when_unset(self, monkeypatch):
        from connectors.rest_connector import (
            _DEFAULT_REST_MAX_RESPONSE_BYTES,
            _resolve_max_response_bytes,
        )

        monkeypatch.delenv("DATA_BOAR_REST_MAX_RESPONSE_BYTES", raising=False)
        assert _resolve_max_response_bytes() == _DEFAULT_REST_MAX_RESPONSE_BYTES

    def test_invalid_env_falls_back_to_default(self, monkeypatch):
        from connectors.rest_connector import (
            _DEFAULT_REST_MAX_RESPONSE_BYTES,
            _resolve_max_response_bytes,
        )

        monkeypatch.setenv("DATA_BOAR_REST_MAX_RESPONSE_BYTES", "not-an-int")
        # Invalid env must never make the cap "unbounded".
        assert _resolve_max_response_bytes() == _DEFAULT_REST_MAX_RESPONSE_BYTES

    def test_clamps_below_floor(self, monkeypatch):
        from connectors.rest_connector import (
            _HARD_MIN_REST_MAX_RESPONSE_BYTES,
            _resolve_max_response_bytes,
        )

        monkeypatch.setenv("DATA_BOAR_REST_MAX_RESPONSE_BYTES", "1")
        assert _resolve_max_response_bytes() == _HARD_MIN_REST_MAX_RESPONSE_BYTES

    def test_clamps_above_ceiling(self, monkeypatch):
        from connectors.rest_connector import (
            _HARD_MAX_REST_MAX_RESPONSE_BYTES,
            _resolve_max_response_bytes,
        )

        monkeypatch.setenv("DATA_BOAR_REST_MAX_RESPONSE_BYTES", str(10**12))
        assert _resolve_max_response_bytes() == _HARD_MAX_REST_MAX_RESPONSE_BYTES


# ---------------------------------------------------------------------------
# _read_bounded_response_body: streamed cap with httpx mocked
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _has_module("httpx"), reason="httpx not installed")
class TestBoundedResponseRead:
    """Exercise the streaming guard without opening real sockets."""

    def _make_streamed_client(self, body_chunks, headers=None, status=200):
        """Return a mock `client` whose `stream()` yields the given chunks."""

        class _StreamCM:
            def __init__(self, chunks, hdrs, st):
                self._chunks = chunks
                self.headers = hdrs or {}
                self.status_code = st
                self.encoding = "utf-8"

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def iter_bytes(self):
                yield from self._chunks

        client = MagicMock()
        client.stream.return_value = _StreamCM(body_chunks, headers, status)
        return client

    def test_refuses_when_content_length_exceeds_cap(self):
        from connectors.rest_connector import (
            _ResponseTooLarge,
            _read_bounded_response_body,
        )

        client = self._make_streamed_client(
            [b""], headers={"Content-Length": str(10_000_000)}
        )
        with pytest.raises(_ResponseTooLarge):
            _read_bounded_response_body(client, "/big", max_bytes=1024)

    def test_refuses_when_streamed_bytes_exceed_cap(self):
        from connectors.rest_connector import (
            _ResponseTooLarge,
            _read_bounded_response_body,
        )

        # No Content-Length advertised; server tries to stream past the cap.
        client = self._make_streamed_client(
            [b"x" * 600, b"x" * 600],  # 1200 bytes total, cap is 1000
            headers={},
        )
        with pytest.raises(_ResponseTooLarge):
            _read_bounded_response_body(client, "/sneaky", max_bytes=1000)

    def test_returns_body_when_within_cap(self):
        from connectors.rest_connector import _read_bounded_response_body

        body = json.dumps({"id": 1, "email": "x@y.co"}).encode("utf-8")
        client = self._make_streamed_client(
            [body],
            headers={"Content-Length": str(len(body))},
        )
        resp = _read_bounded_response_body(client, "/ok", max_bytes=1024)
        assert resp.status_code == 200
        assert resp.json() == {"id": 1, "email": "x@y.co"}


# ---------------------------------------------------------------------------
# RESTConnector.run(): demotion is logged, scan continues
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _has_module("httpx"), reason="httpx not installed")
class TestRESTConnectorOversizeDemotion:
    """The connector must call save_failure with a clear reason on oversize."""

    def test_oversize_path_records_failure_and_continues(self, monkeypatch):
        from connectors.rest_connector import RESTConnector

        target = {
            "name": "chaos-api",
            "type": "api",
            "base_url": "http://example.test",
            "paths": ["/huge", "/ok"],
            "connect_timeout_seconds": 5,
            "read_timeout_seconds": 5,
        }

        scanner = MagicMock()
        scanner.scan_column.return_value = {
            "sensitivity_level": "LOW",
            "pattern_detected": "",
            "norm_tag": "",
            "ml_confidence": 0,
        }
        db = MagicMock()

        def fake_bounded(client, path, max_bytes):
            from connectors.rest_connector import _BoundedResponse, _ResponseTooLarge

            if path == "/huge":
                raise _ResponseTooLarge(max_bytes, f">{max_bytes} bytes streamed")
            body = json.dumps({"id": 1}).encode("utf-8")
            return _BoundedResponse(200, body, "utf-8")

        connector = RESTConnector(target, scanner, db)
        with (
            patch("connectors.rest_connector.httpx.Client") as mock_client_cls,
            patch(
                "connectors.rest_connector._read_bounded_response_body",
                side_effect=fake_bounded,
            ),
        ):
            mock_client_cls.return_value = MagicMock()
            connector.run()

        # /huge was refused with a clear demotion reason; /ok still ran.
        failure_calls = [c.args for c in db.save_failure.call_args_list]
        assert any(
            "GET /huge" in args[2] and "response cap" in args[2]
            for args in failure_calls
        ), f"expected response-cap failure for /huge, got {failure_calls!r}"
        # Connector continued to /ok and called the scanner for it.
        assert scanner.scan_column.called

    def test_discover_url_oversize_is_refused(self):
        from connectors.rest_connector import RESTConnector

        target = {
            "name": "chaos-api",
            "type": "api",
            "base_url": "http://example.test",
            "discover_url": "/discover",
            "connect_timeout_seconds": 5,
            "read_timeout_seconds": 5,
        }
        scanner = MagicMock()
        db = MagicMock()

        def fake_bounded(client, path, max_bytes):
            from connectors.rest_connector import _ResponseTooLarge

            raise _ResponseTooLarge(max_bytes, "Content-Length=999999999")

        connector = RESTConnector(target, scanner, db)
        with (
            patch("connectors.rest_connector.httpx.Client") as mock_client_cls,
            patch(
                "connectors.rest_connector._read_bounded_response_body",
                side_effect=fake_bounded,
            ),
        ):
            mock_client_cls.return_value = MagicMock()
            connector.run()

        failure_calls = [c.args for c in db.save_failure.call_args_list]
        assert any(
            "Discover refused" in args[2] and "response cap" in args[2]
            for args in failure_calls
        ), f"expected discover refusal, got {failure_calls!r}"
