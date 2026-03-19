from __future__ import annotations

import os
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

    # Optional environment override: Docker images can set API_HOST=0.0.0.0 so the
    # container is reachable from outside via port bindings, while CLI/desktop
    # remains safely on 127.0.0.1 by default.
    env_host = (os.environ.get("API_HOST") or "").strip()
    if env_host:
        return env_host

    # Safer default for desktop/CLI: bind only to loopback unless explicitly overridden.
    return "127.0.0.1"
