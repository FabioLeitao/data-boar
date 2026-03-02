"""Tests for connector registry and engine (no live DB/FS required)."""
import pytest

# Ensure connectors register themselves (registry is populated on import)
import connectors.filesystem_connector  # noqa: F401
import connectors.sql_connector  # noqa: F401

from core.connector_registry import connector_for_target, list_connector_types


def test_registry_has_sql_and_filesystem():
    types = list_connector_types()
    assert "filesystem" in types
    assert "postgresql" in types or "mysql" in types


def test_connector_for_filesystem():
    target = {"type": "filesystem", "path": "/tmp", "name": "FS"}
    resolved = connector_for_target(target)
    assert resolved is not None
    cls, _ = resolved
    assert cls is not None


def test_connector_for_database_postgres():
    target = {"type": "database", "driver": "postgresql+psycopg2", "name": "PG", "host": "localhost"}
    resolved = connector_for_target(target)
    assert resolved is not None


def test_connector_for_unknown():
    target = {"type": "database", "driver": "unknown_db", "name": "X"}
    resolved = connector_for_target(target)
    assert resolved is None
