from __future__ import annotations

from core.host_resolution import resolve_api_host


def test_resolve_api_host_prefers_cli_host_when_provided() -> None:
    config = {"api": {"host": "1.2.3.4"}}
    assert resolve_api_host(config, cli_host="127.0.0.1") == "127.0.0.1"


def test_resolve_api_host_uses_config_host_when_cli_missing() -> None:
    config = {"api": {"host": "10.0.0.1"}}
    assert resolve_api_host(config, cli_host=None) == "10.0.0.1"


def test_resolve_api_host_falls_back_to_loopback_default() -> None:
    config = {"api": {}}
    assert resolve_api_host(config, cli_host=None) == "127.0.0.1"


def test_resolve_api_host_handles_missing_api_block() -> None:
    config = {}
    assert resolve_api_host(config, cli_host=None) == "127.0.0.1"


def test_resolve_api_host_uses_env_api_host_when_no_config() -> None:
    import os

    old = os.environ.get("API_HOST")
    try:
        os.environ["API_HOST"] = "0.0.0.0"
        assert resolve_api_host({}, cli_host=None) == "0.0.0.0"
    finally:
        if old is None:
            os.environ.pop("API_HOST", None)
        else:
            os.environ["API_HOST"] = old
