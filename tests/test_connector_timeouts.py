"""
Tests for configurable timeouts: connector wiring uses connect_timeout_seconds and
read_timeout_seconds from target config (normalized by config loader with global + per-target).
No live connections; mocks used where needed.
"""
import pytest
from unittest.mock import MagicMock, patch

from config.loader import normalize_config


def test_normalized_targets_have_timeout_seconds():
    """After normalization, each target has connect_timeout_seconds and read_timeout_seconds."""
    cfg = normalize_config({
        "targets": [
            {"name": "a", "type": "database", "driver": "postgresql", "host": "h", "database": "d"},
            {"name": "b", "type": "api", "base_url": "http://x"},
        ],
        "timeouts": {"connect_seconds": 20, "read_seconds": 80},
    })
    for t in cfg["targets"]:
        assert "connect_timeout_seconds" in t
        assert "read_timeout_seconds" in t
        assert t["connect_timeout_seconds"] >= 1
        assert t["read_timeout_seconds"] >= 1


def test_rest_connector_uses_httpx_timeout_from_config():
    """REST connector connect() builds httpx.Timeout(connect=..., read=...) from target config."""
    try:
        import httpx
    except ImportError:
        pytest.skip("httpx not installed")
    from connectors.rest_connector import RESTConnector

    target = {
        "name": "test-api",
        "type": "api",
        "base_url": "http://example.com",
        "connect_timeout_seconds": 10,
        "read_timeout_seconds": 60,
    }
    connector = RESTConnector(target, MagicMock(), MagicMock())
    with patch("connectors.rest_connector.httpx.Client") as mock_client:
        connector.connect()
        mock_client.assert_called_once()
        call_kw = mock_client.call_args[1]
        timeout = call_kw.get("timeout")
        assert timeout is not None
        assert isinstance(timeout, httpx.Timeout)
        assert timeout.connect == 10
        assert timeout.read == 60


def test_rest_connector_timeout_defaults_when_not_in_config():
    """REST connector uses defaults 25/90 when timeout keys missing from target."""
    try:
        import httpx
    except ImportError:
        pytest.skip("httpx not installed")
    from connectors.rest_connector import RESTConnector

    target = {"name": "api", "type": "api", "base_url": "http://example.com"}
    # Simulate loader having merged defaults onto target
    target["connect_timeout_seconds"] = 25
    target["read_timeout_seconds"] = 90
    connector = RESTConnector(target, MagicMock(), MagicMock())
    with patch("connectors.rest_connector.httpx.Client") as mock_client:
        connector.connect()
        timeout = mock_client.call_args[1]["timeout"]
        assert timeout.connect == 25
        assert timeout.read == 90


def test_mongodb_connector_receives_timeout_params():
    """MongoDB connector connect() passes serverSelectionTimeoutMS, connectTimeoutMS, socketTimeoutMS."""
    try:
        from pymongo import MongoClient
    except ImportError:
        pytest.skip("pymongo not installed")
    from connectors.mongodb_connector import MongoDBConnector

    target = {
        "name": "mongo",
        "type": "database",
        "driver": "mongodb",
        "host": "localhost",
        "port": 27017,
        "database": "test",
        "connect_timeout_seconds": 15,
        "read_timeout_seconds": 45,
    }
    connector = MongoDBConnector(target, MagicMock(), MagicMock())
    with patch("connectors.mongodb_connector.MongoClient") as mock_mongo:
        mock_mongo.return_value = MagicMock()
        connector.connect()
        mock_mongo.assert_called_once()
        call_kw = mock_mongo.call_args[1]
        assert call_kw["serverSelectionTimeoutMS"] == 15_000
        assert call_kw["connectTimeoutMS"] == 15_000
        assert call_kw["socketTimeoutMS"] == 45_000
        connector.close()


def test_redis_connector_receives_socket_timeouts():
    """Redis connector connect() passes socket_connect_timeout and socket_timeout."""
    try:
        import redis
    except ImportError:
        pytest.skip("redis not installed")
    from connectors.redis_connector import RedisConnector

    target = {
        "name": "redis",
        "type": "database",
        "driver": "redis",
        "host": "localhost",
        "port": 6379,
        "connect_timeout_seconds": 10,
        "read_timeout_seconds": 30,
    }
    connector = RedisConnector(target, MagicMock(), MagicMock())
    with patch("connectors.redis_connector.redis.Redis") as mock_redis:
        mock_redis.return_value = MagicMock()
        connector.connect()
        mock_redis.assert_called_once()
        call_kw = mock_redis.call_args[1]
        assert call_kw["socket_connect_timeout"] == 10
        assert call_kw["socket_timeout"] == 30
        connector.close()


def test_sql_connector_connect_calls_create_engine_with_connect_args(tmp_path):
    """SQL connector connect() passes connect_args from target timeouts."""
    from connectors.sql_connector import SQLConnector

    db_path = str(tmp_path / "t.db")
    target = {
        "name": "sqlite-test",
        "type": "database",
        "driver": "sqlite",
        "database": db_path,
        "connect_timeout_seconds": 5,
        "read_timeout_seconds": 20,
    }
    connector = SQLConnector(target, MagicMock(), MagicMock())
    with patch("connectors.sql_connector.create_engine") as mock_create:
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value = mock_conn
        mock_create.return_value = mock_engine
        connector.connect()
        mock_create.assert_called_once()
        call_kw = mock_create.call_args[1]
        assert "connect_args" in call_kw
        assert call_kw["connect_args"]["timeout"] == 20
    connector.close()
