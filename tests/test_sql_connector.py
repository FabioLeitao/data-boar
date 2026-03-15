"""Tests for SQL connector discover/run refactors (cognitive complexity S3776).

Ensures refactored helpers _get_skip_schemas, _should_skip_schema, _tables_from_schema,
_discover_fallback_no_schemas preserve behavior so discover() returns expected tables/columns.
"""
import sqlite3
from unittest.mock import MagicMock

from connectors.sql_connector import (
    SQLConnector,
    _connect_args_from_target,
    _discover_fallback_no_schemas,
    _get_skip_schemas,
    _should_skip_schema,
)
from sqlalchemy import create_engine, inspect


def test_get_skip_schemas_oracle_uses_system_schemas():
    """_get_skip_schemas('oracle') returns Oracle system set."""
    skip = _get_skip_schemas("oracle")
    assert "SYS" in skip
    assert "SYSTEM" in skip


def test_get_skip_schemas_non_oracle_uses_default():
    """_get_skip_schemas for postgresql/mysql returns default skip set."""
    skip = _get_skip_schemas("postgresql")
    assert "information_schema" in skip
    assert "pg_catalog" in skip


def test_should_skip_schema_empty():
    """_should_skip_schema returns True for None or empty."""
    assert _should_skip_schema(None, "postgresql", set()) is True
    assert _should_skip_schema("", "postgresql", set()) is True


def test_should_skip_schema_when_in_set():
    """_should_skip_schema returns True when schema is in skip_schemas."""
    assert _should_skip_schema("information_schema", "postgresql", {"information_schema"}) is True
    assert _should_skip_schema("SYS", "oracle", {"SYS"}) is True


def test_should_skip_schema_oracle_uppercase():
    """Oracle dialect: comparison uses schema.upper()."""
    assert _should_skip_schema("sys", "oracle", {"SYS"}) is True


def test_sql_connector_discover_sqlite_in_memory(tmp_path):
    """SQLConnector.discover() with in-memory SQLite returns tables (fallback path)."""
    db_path = tmp_path / "audit.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE t1 (a TEXT, b INTEGER)")
    conn.execute("CREATE TABLE t2 (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

    target = {"type": "database", "driver": "sqlite", "database": str(db_path), "name": "TestDB"}
    scanner = MagicMock()
    db_manager = MagicMock()
    connector = SQLConnector(target, scanner, db_manager)
    connector.connect()
    try:
        result = connector.discover()
    finally:
        connector.close()

    assert len(result) >= 2
    tables = {r["table"] for r in result}
    assert "t1" in tables
    assert "t2" in tables
    t1 = next(r for r in result if r["table"] == "t1")
    # SQLite file DB may report schema "main" or ""
    assert t1["schema"] in ("", "main")
    col_names = [c["name"] for c in t1["columns"]]
    assert "a" in col_names
    assert "b" in col_names


def test_discover_fallback_no_schemas_returns_list():
    """_discover_fallback_no_schemas returns a list (empty or with tables)."""
    engine = create_engine("sqlite:///:memory:")
    inspector = inspect(engine)
    out = _discover_fallback_no_schemas(inspector)
    assert isinstance(out, list)
    engine.dispose()


def test_connect_args_from_target_postgresql():
    """_connect_args_from_target returns connect_timeout and statement_timeout for PostgreSQL."""
    target = {"driver": "postgresql", "connect_timeout_seconds": 15, "read_timeout_seconds": 120}
    args = _connect_args_from_target(target)
    assert args["connect_timeout"] == 15
    assert "options" in args
    assert "statement_timeout=120000" in args["options"]


def test_connect_args_from_target_mysql():
    """_connect_args_from_target returns connect_timeout for MySQL."""
    target = {"driver": "mysql", "connect_timeout_seconds": 10, "read_timeout_seconds": 60}
    args = _connect_args_from_target(target)
    assert args["connect_timeout"] == 10
    assert "options" not in args


def test_connect_args_from_target_sqlite():
    """_connect_args_from_target returns timeout (lock wait) for SQLite."""
    target = {"driver": "sqlite", "read_timeout_seconds": 30}
    args = _connect_args_from_target(target)
    assert args["timeout"] == 30


def test_connect_args_from_target_defaults():
    """_connect_args_from_target uses defaults 25/90 when keys missing."""
    target = {"driver": "postgresql"}
    args = _connect_args_from_target(target)
    assert args["connect_timeout"] == 25
    assert "statement_timeout=90000" in args["options"]


def test_connect_args_from_target_clamped():
    """_connect_args_from_target clamps timeouts to at least 1."""
    target = {"driver": "mysql", "connect_timeout_seconds": 0, "read_timeout_seconds": -1}
    args = _connect_args_from_target(target)
    assert args["connect_timeout"] >= 1
