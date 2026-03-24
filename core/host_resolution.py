from __future__ import annotations

import os
from typing import Any


def resolve_api_host(config: dict[str, Any], cli_host: str | None = None) -> str:
    """
    Resolve the host/interface for the API server.

    Resolution order:
    - If cli_host is provided (e.g. main.py --web --host), prefer it.
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


def api_bind_exposes_non_loopback(host: str) -> bool:
    """
    True when the API listens beyond loopback (e.g. 0.0.0.0, LAN IP, ::), so clients on
    other hosts can reach the service without SSH port forwarding.
    """
    h = (host or "").strip().lower()
    if not h:
        return False
    if h in ("127.0.0.1", "::1", "localhost"):
        return False
    return True


def should_warn_insecure_api_bind(config: dict[str, Any], host: str) -> bool:
    """
    Wabbix / SECURITY: warn when the bind address is reachable beyond loopback but API key
    is not effectively required (open scan/config surface on untrusted networks).
    """
    if not api_bind_exposes_non_loopback(host):
        return False
    api_cfg = config.get("api")
    if not isinstance(api_cfg, dict):
        api_cfg = {}
    if bool(api_cfg.get("require_api_key")):
        key = (api_cfg.get("api_key") or "").strip()
        if key:
            return False
    return True
