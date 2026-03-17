from __future__ import annotations

from typing import Any


def resolve_api_host(config: dict[str, Any], cli_host: str | None = None) -> str:
    """
    Resolve the host/interface for the API server.

    Phase 1 (no behaviour change): reproduce existing behaviour in one place.
    - If cli_host is provided (future CLI flag), prefer it.
    - Else, if config.api.host is set, use it.
    - Else, fall back to the historical default: "0.0.0.0".

    Later phases can safely adjust the default (e.g. to 127.0.0.1 for desktop)
    while tests assert the intended behaviour.
    """

    if cli_host:
        return cli_host
    api_cfg = config.get("api") or {}
    host = (api_cfg.get("host") or "").strip()
    if host:
        return host
    # Historical default: bind to all interfaces.
    return "0.0.0.0"

