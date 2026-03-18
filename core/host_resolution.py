from __future__ import annotations

from typing import Any


def resolve_api_host(config: dict[str, Any], cli_host: str | None = None) -> str:
    """
    Resolve the host/interface for the API server.

    Resolution order:
    - If cli_host is provided (future CLI flag), prefer it.
    - Else, if config.api.host is set, use it.
    - Else, fall back to a safer desktop default: "127.0.0.1".

    Containers and orchestrated deployments (Docker/Kubernetes) should set an
    explicit api.host or use container-level port bindings when they need to
    expose the service on 0.0.0.0.
    """

    if cli_host:
        return cli_host
    api_cfg = config.get("api") or {}
    host = (api_cfg.get("host") or "").strip()
    if host:
        return host
    # Safer default for desktop/CLI: bind only to loopback unless explicitly overridden.
    return "127.0.0.1"
