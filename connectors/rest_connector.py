"""
REST/API connector: call remote HTTP(S) endpoints with configurable authentication
(basic, bearer token, OAuth2 client credentials, or custom headers) to discover
and scan response payloads for personal or sensitive data.
Optional: register only when httpx is available. Used for type "api" or "rest" targets.

SRE / chaos-audit notes (`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`,
`THE_ART_OF_THE_FALLBACK.md`):

- Every response read is **bounded** by ``DATA_BOAR_REST_MAX_RESPONSE_BYTES``
  (default 25 MiB). Both ``Content-Length``-advertised oversize bodies and bodies
  that grow past the cap mid-stream are refused before they fill memory.
- The JSON walk in :func:`_flatten_sample` is depth- and width-bounded so
  adversarial nesting (``{"a": {"a": {"a": ...}}}``) cannot trigger
  ``RecursionError`` and a million-key dictionary cannot pin a CPU.
- Truncation never falls through silently: a ``__truncated__`` row is emitted
  in the flattened output and (when a `db_manager` is wired) ``save_failure``
  records the demotion reason — same contract as
  ``THE_ART_OF_THE_FALLBACK.md`` §3 ("diagnostic on fall").
"""

import os
from typing import Any
import json

from core.about import get_http_user_agent
from core.connector_registry import register
from core.suggested_review import (
    SUGGESTED_REVIEW_PATTERN,
    augment_low_id_like_for_persist,
)

try:
    import httpx

    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False
    httpx = None


# Defensive caps. Operators can tighten via env; the runtime clamps to safe ranges
# so a misconfiguration cannot remove the cap entirely.
_ENV_REST_MAX_RESPONSE_BYTES = "DATA_BOAR_REST_MAX_RESPONSE_BYTES"
_DEFAULT_REST_MAX_RESPONSE_BYTES = 25 * 1024 * 1024  # 25 MiB
_HARD_MIN_REST_MAX_RESPONSE_BYTES = 4 * 1024  # 4 KiB floor (protect against typos)
_HARD_MAX_REST_MAX_RESPONSE_BYTES = 512 * 1024 * 1024  # 512 MiB ceiling

# JSON walk caps for `_flatten_sample`. Depth 32 absorbs realistic OpenAPI nesting;
# 200 keys per object is well past anything a sane API exposes per resource.
_DEFAULT_FLATTEN_MAX_DEPTH = 32
_DEFAULT_FLATTEN_MAX_KEYS_PER_LEVEL = 200
# Hard total-row ceiling so a wide flat dict still cannot blow up memory.
_DEFAULT_FLATTEN_MAX_TOTAL_ROWS = 5000


def _resolve_max_response_bytes() -> int:
    """Resolve the per-response byte cap from env, clamped to the hard range."""
    raw = (os.environ.get(_ENV_REST_MAX_RESPONSE_BYTES) or "").strip()
    if not raw:
        return _DEFAULT_REST_MAX_RESPONSE_BYTES
    try:
        v = int(raw)
    except ValueError:
        return _DEFAULT_REST_MAX_RESPONSE_BYTES
    return max(
        _HARD_MIN_REST_MAX_RESPONSE_BYTES,
        min(v, _HARD_MAX_REST_MAX_RESPONSE_BYTES),
    )


class _ResponseTooLarge(Exception):
    """Raised when an HTTP response exceeds the configured byte cap."""

    def __init__(self, limit_bytes: int, observed: str):
        super().__init__(
            f"response exceeded {limit_bytes} byte cap (observed {observed})"
        )
        self.limit_bytes = limit_bytes
        self.observed = observed


class _BoundedResponse:
    """
    Minimal response wrapper used by the connector after a bounded streamed read.

    Mirrors the small surface :class:`RESTConnector` actually consumes
    (``status_code``, ``raise_for_status``, ``json``, ``text``) so the rest of
    the connector stays oblivious to whether we used streaming or a one-shot GET.
    """

    def __init__(self, status_code: int, body: bytes, encoding: str | None):
        self.status_code = int(status_code)
        self._body = body
        self._encoding = encoding or "utf-8"

    def raise_for_status(self) -> None:
        if 400 <= self.status_code:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=None,  # type: ignore[arg-type]
                response=None,  # type: ignore[arg-type]
            )

    @property
    def text(self) -> str:
        try:
            return self._body.decode(self._encoding, errors="replace")
        except (LookupError, TypeError):
            return self._body.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text)


def _read_bounded_response_body(
    client: "httpx.Client", path_str: str, max_bytes: int
) -> _BoundedResponse:
    """
    Stream a GET and refuse bodies above ``max_bytes``.

    The Content-Length pre-check fails fast (no body read) when the server
    advertises an oversized payload; servers that omit the header still get
    bounded by the streamed read so we never buffer more than ``max_bytes + 1``.
    Raises :class:`_ResponseTooLarge` when the cap is exceeded.
    """
    with client.stream("GET", path_str) as response:
        cl_header = response.headers.get("Content-Length")
        if cl_header is not None:
            try:
                advertised = int(cl_header)
            except (TypeError, ValueError):
                advertised = None
            if advertised is not None and advertised > max_bytes:
                raise _ResponseTooLarge(max_bytes, f"Content-Length={advertised}")
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_bytes():
            total += len(chunk)
            if total > max_bytes:
                raise _ResponseTooLarge(max_bytes, f">{max_bytes} bytes streamed")
            chunks.append(chunk)
        encoding = response.encoding or "utf-8"
        status_code = response.status_code
    return _BoundedResponse(status_code, b"".join(chunks), encoding)


def _build_auth(client: "httpx.Client", target: dict[str, Any]) -> None:
    """
    Configure auth on the client from target["auth"].
    Supports: basic (username/password), bearer (token), oauth2_client (token_url, client_id, client_secret),
    custom (headers with Authorization or other). Negotiated tokens (e.g. Kerberos) can be passed via custom.
    """
    auth = target.get("auth") or {}
    auth_type = (auth.get("type") or "none").lower()

    if auth_type == "basic":
        username = auth.get("username", auth.get("user", ""))
        password = auth.get("password", auth.get("pass", ""))
        if username or password:
            client.auth = httpx.BasicAuth(username, password)
        return

    if auth_type == "bearer":
        token = auth.get("token") or (
            os.environ.get(auth.get("token_from_env", ""))
            if auth.get("token_from_env")
            else None
        )
        if token:
            client.headers["Authorization"] = f"Bearer {token}"
        return

    if auth_type == "oauth2_client":
        token_url = auth.get("token_url")
        client_id = auth.get("client_id", "")
        client_secret = auth.get("client_secret", "")
        if (
            isinstance(client_secret, str)
            and client_secret.startswith("${")
            and client_secret.endswith("}")
        ):
            client_secret = os.environ.get(client_secret[2:-1], "")
        scope = auth.get("scope", "")
        if token_url and client_id and client_secret:
            # One-off request to token endpoint (no client auth)
            resp = httpx.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    **({"scope": scope} if scope else {}),
                },
                headers={
                    "Accept": "application/json",
                    "User-Agent": get_http_user_agent(),
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            access_token = data.get("access_token")
            if access_token:
                client.headers["Authorization"] = f"Bearer {access_token}"
        return

    if auth_type == "custom":
        for key, value in (auth.get("headers") or {}).items():
            if value is not None:
                client.headers[key] = str(value)
        return

    # Static username/password in target (no auth block): use as Basic
    user = target.get("user", target.get("username", ""))
    password = target.get("pass", target.get("password", ""))
    if user or password:
        client.auth = httpx.BasicAuth(user, password)


def _scalar_to_connector_data_type(value: Any, max_varchar: int = 4000) -> str | None:
    """
    Infer SQL-style declared type from JSON scalars for Plan §4 ``connector_format_id_hint``.

    Integers map to BIGINT; strings map to VARCHAR(n) capped by ``max_varchar`` (sample length).
    Booleans and floats are skipped (no stable schema hint).
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return "BIGINT"
    if isinstance(value, float):
        return None
    if isinstance(value, str):
        n = min(len(value), max_varchar)
        return f"VARCHAR({max(n, 1)})"
    return None


def _flatten_sample(
    obj: Any,
    prefix: str = "",
    max_len: int = 500,
    *,
    max_depth: int = _DEFAULT_FLATTEN_MAX_DEPTH,
    max_keys_per_level: int = _DEFAULT_FLATTEN_MAX_KEYS_PER_LEVEL,
    max_total_rows: int = _DEFAULT_FLATTEN_MAX_TOTAL_ROWS,
) -> list[tuple[str, str, Any | None]]:
    """
    Recursively flatten JSON-like structure into ``(key_path, string_value, raw_scalar)``.

    ``raw_scalar`` is the leaf JSON value before string coercion when applicable
    (used with :func:`_scalar_to_connector_data_type`). Non-leaf paths use ``None``.

    **Defensive caps** (chaos-audit hardening — see module docstring):

    - ``max_depth`` bounds JSON nesting; a deeper path emits a single
      ``__truncated__`` audit row instead of raising :class:`RecursionError`.
    - ``max_keys_per_level`` bounds object width; extra keys past the cap also
      surface as ``__truncated__`` so reviewers know we stopped intentionally.
    - ``max_total_rows`` bounds the total flattened output, protecting the
      detector loop downstream from pathological payloads.

    A trailing :class:`RecursionError` guard is the belt-and-suspenders fallback
    in case a future caller forgets to lower ``max_depth`` below the host limit.
    """

    out: list[tuple[str, str, Any | None]] = []
    truncated_reasons: set[str] = set()

    def _record_truncation(reason: str, path: str) -> None:
        if reason in truncated_reasons:
            return
        truncated_reasons.add(reason)
        out.append((path or "value", reason, None))

    def _walk(value: Any, key_prefix: str, depth: int) -> None:
        if len(out) >= max_total_rows:
            _record_truncation(
                f"max_total_rows={max_total_rows}", key_prefix or (prefix or "value")
            )
            return
        if depth > max_depth:
            _record_truncation(
                f"max_depth={max_depth}", key_prefix or (prefix or "value")
            )
            return
        if value is None:
            out.append((key_prefix or "value", "", None))
            return
        if isinstance(value, bool):
            out.append((key_prefix or "value", "true" if value else "false", value))
            return
        if isinstance(value, int):
            out.append((key_prefix or "value", str(value)[:max_len], value))
            return
        if isinstance(value, float):
            out.append((key_prefix or "value", str(value)[:max_len], value))
            return
        if isinstance(value, str):
            out.append((key_prefix or "value", value[:max_len], value))
            return
        if isinstance(value, list):
            for i, item in enumerate(value[:3]):
                if len(out) >= max_total_rows:
                    _record_truncation(
                        f"max_total_rows={max_total_rows}",
                        key_prefix or (prefix or "value"),
                    )
                    return
                child_prefix = f"{key_prefix}[{i}]" if key_prefix else f"[{i}]"
                _walk(item, child_prefix, depth + 1)
            return
        if isinstance(value, dict):
            items = list(value.items())
            if len(items) > max_keys_per_level:
                _record_truncation(
                    f"max_keys_per_level={max_keys_per_level}",
                    key_prefix or (prefix or "value"),
                )
                items = items[:max_keys_per_level]
            for k, v in items:
                if len(out) >= max_total_rows:
                    _record_truncation(
                        f"max_total_rows={max_total_rows}",
                        key_prefix or (prefix or "value"),
                    )
                    return
                key = f"{key_prefix}.{k}" if key_prefix else str(k)
                if isinstance(v, (dict, list)) and v:
                    _walk(v, key, depth + 1)
                elif v is None:
                    out.append((key, "", None))
                elif isinstance(v, (dict, list)) and not v:
                    out.append((key, str(v)[:max_len], None))
                else:
                    out.append((key, str(v)[:max_len], v))
            return
        out.append((key_prefix or "value", str(value)[:max_len], None))

    try:
        _walk(obj, prefix, 0)
    except RecursionError:
        # Belt-and-suspenders: if max_depth was misconfigured above the host
        # recursion limit, still degrade gracefully with an audit row instead
        # of crashing the connector.
        _record_truncation("recursion_limit_reached", prefix or "value")

    return out


class RESTConnector:
    """
    Connect to REST/API endpoints with configurable auth (basic, bearer, OAuth2 client, custom headers),
    GET configured paths, parse JSON responses, and run sensitivity detection on field names and sample values.
    Findings are saved as filesystem_findings with file_name encoding path and field (e.g. "GET /users | email").
    """

    def __init__(
        self,
        target_config: dict[str, Any],
        scanner: Any,
        db_manager: Any,
        sample_limit: int = 5,
        detection_config: dict[str, Any] | None = None,
    ):
        self.config = target_config
        self.scanner = scanner
        self.db_manager = db_manager
        self.sample_limit = sample_limit
        self.detection_config = detection_config or {}
        self._client: "httpx.Client | None" = None

    def connect(self) -> None:
        if not _HTTPX_AVAILABLE:
            raise RuntimeError(
                "httpx is required for REST connector. Install with: pip install httpx"
            )
        base_url = (self.config.get("base_url") or self.config.get("url", "")).rstrip(
            "/"
        )
        connect_s = float(self.config.get("connect_timeout_seconds", 25))
        read_s = float(self.config.get("read_timeout_seconds", 90))
        # Default (first arg) used for write/pool; connect and read set explicitly (httpx requires default or all four).
        timeout = httpx.Timeout(read_s, connect=connect_s, read=read_s)
        cfg_headers = self.config.get("headers") or {}
        has_ua = any(str(k).lower() == "user-agent" for k in cfg_headers)
        default_headers: dict[str, str] = {}
        if not has_ua:
            default_headers["User-Agent"] = get_http_user_agent()
        self._client = httpx.Client(
            base_url=base_url, timeout=timeout, headers=default_headers or None
        )
        _build_auth(self._client, self.config)
        # Optional extra headers (e.g. API key, negotiated token); may override User-Agent.
        for key, value in cfg_headers.items():
            if value is not None:
                self._client.headers[str(key)] = str(value)

    def close(self) -> None:
        if self._client:
            try:
                self._client.close()
            except Exception:
                # Best-effort close: ignore client shutdown errors.
                return
            self._client = None

    def run(self) -> None:
        if not _HTTPX_AVAILABLE:
            self.db_manager.save_failure(
                self.config.get("name", "api"),
                "error",
                "httpx not installed. Install with: pip install httpx",
            )
            return
        self.connect()
        max_bytes = _resolve_max_response_bytes()
        try:
            paths = self.config.get("paths") or self.config.get("endpoints") or []
            discover_url = self.config.get("discover_url")
            if discover_url and not paths:
                try:
                    r = _read_bounded_response_body(
                        self._client, discover_url, max_bytes
                    )
                    r.raise_for_status()
                    data = r.json()
                    if isinstance(data, list):
                        paths = [
                            p if isinstance(p, str) else p.get("path", p.get("url", ""))
                            for p in data
                        ]
                    elif isinstance(data, dict) and "paths" in data:
                        paths = data["paths"]
                    elif isinstance(data, dict) and "endpoints" in data:
                        paths = data["endpoints"]
                except _ResponseTooLarge as e:
                    # Manifesto §3 ("diagnostic on fall"): refuse big payloads
                    # before they fill memory and log the demotion reason.
                    self.db_manager.save_failure(
                        self.config.get("name", "api"),
                        "error",
                        f"Discover refused: response cap ({e.observed} > {e.limit_bytes} bytes)",
                    )
                    return
                except Exception as e:
                    self.db_manager.save_failure(
                        self.config.get("name", "api"), "error", f"Discover failed: {e}"
                    )
                    return
            if not paths:
                self.db_manager.save_failure(
                    self.config.get("name", "api"),
                    "error",
                    "No paths or discover_url configured",
                )
                return
            target_name = self.config.get("name", "API")
            self._save_inventory_snapshot(target_name)
            seen_path_key: set[tuple[str, str]] = (
                set()
            )  # (path_str, key) to avoid duplicate findings per field
            for path in paths:
                path_str = (
                    path
                    if isinstance(path, str)
                    else path.get("path", path.get("url", ""))
                )
                if not path_str:
                    continue
                path_str = path_str if path_str.startswith("/") else "/" + path_str
                try:
                    r = _read_bounded_response_body(self._client, path_str, max_bytes)
                    r.raise_for_status()
                except _ResponseTooLarge as e:
                    # Manifesto §3: log the demotion reason; never silently drop
                    # a path because it was too big.
                    self.db_manager.save_failure(
                        target_name,
                        "error",
                        f"GET {path_str}: response cap ({e.observed} > {e.limit_bytes} bytes)",
                    )
                    continue
                except Exception as e:
                    self.db_manager.save_failure(
                        target_name, "error", f"GET {path_str}: {e}"
                    )
                    continue
                try:
                    payload = r.json()
                except Exception:
                    payload = {"_raw": r.text[:2000]}

                def _save_if_sensitive(
                    key: str, sample: str, raw_scalar: Any | None = None
                ) -> None:
                    if (path_str, key) in seen_path_key:
                        return
                    ctype = _scalar_to_connector_data_type(raw_scalar)
                    result = self.scanner.scan_column(
                        key, sample, connector_data_type=ctype
                    )
                    result = augment_low_id_like_for_persist(
                        result, key, self.detection_config
                    )
                    hi_med = result.get("sensitivity_level") in ("HIGH", "MEDIUM")
                    suggested = (
                        result.get("pattern_detected") == SUGGESTED_REVIEW_PATTERN
                    )
                    if not hi_med and not suggested:
                        return
                    seen_path_key.add((path_str, key))
                    self.db_manager.save_finding(
                        "filesystem",
                        target_name=target_name,
                        path=self.config.get("base_url", "") + path_str,
                        file_name=f"GET {path_str} | {key}",
                        data_type="application/json",
                        sensitivity_level=result.get("sensitivity_level", "MEDIUM"),
                        pattern_detected=result.get("pattern_detected", ""),
                        norm_tag=result.get("norm_tag", ""),
                        ml_confidence=result.get("ml_confidence") or 0,
                    )

                if isinstance(payload, list):
                    for item in payload[: self.sample_limit]:
                        if isinstance(item, dict):
                            for key, sample, raw_scalar in _flatten_sample(
                                item, prefix="", max_len=500
                            ):
                                _save_if_sensitive(key, sample, raw_scalar)
                    if not payload:
                        for key, sample, raw_scalar in _flatten_sample(
                            {}, prefix="(empty)", max_len=500
                        ):
                            _save_if_sensitive(key, sample, raw_scalar)
                else:
                    for key, sample, raw_scalar in _flatten_sample(
                        payload, max_len=500
                    ):
                        _save_if_sensitive(key, sample, raw_scalar)
        finally:
            self.close()

    def _save_inventory_snapshot(self, target_name: str) -> None:
        """Persist one REST/API inventory row with API version hints."""
        if not hasattr(self.db_manager, "save_data_source_inventory"):
            return
        version_hint = (
            self.config.get("api_version")
            or self.config.get("version")
            or self._infer_api_version_from_paths()
        )
        transport = (
            "tls=https"
            if str(self.config.get("base_url", "")).lower().startswith("https://")
            else "unknown"
        )
        details = {
            "base_url": str(
                self.config.get("base_url") or self.config.get("url") or ""
            ),
            "auth_type": str((self.config.get("auth") or {}).get("type") or "none"),
        }
        try:
            self.db_manager.save_data_source_inventory(
                target_name=target_name,
                source_type="api",
                product=self.config.get("product") or "rest-api",
                product_version=None,
                protocol_or_api_version=str(version_hint or "") or None,
                transport_security=transport,
                raw_details=json.dumps(details, ensure_ascii=False),
            )
        except Exception:
            # Inventory snapshot is best-effort; scan should continue without it.
            return

    def _infer_api_version_from_paths(self) -> str | None:
        paths = self.config.get("paths") or self.config.get("endpoints") or []
        for p in paths:
            path_str = p if isinstance(p, str) else p.get("path", p.get("url", ""))
            low = str(path_str).lower()
            for token in ("/v1", "/v2", "/v3", "/v4"):
                if token in low:
                    return token.strip("/")
        return None


if _HTTPX_AVAILABLE:
    register("api", RESTConnector, ["name", "base_url"])
    register("rest", RESTConnector, ["name", "base_url"])
