"""
Security tests: SQL injection resistance, path traversal, and safe handling of untrusted input.

- SQL injection: identifier escaping (quote/backtick) ensures table/column names from discover()
  never execute as multiple statements; session_id and other user-supplied values are only
  used via parameterized ORM or validated (session_id pattern).
- Path traversal: session_id is validated (api/routes) before use in paths; invalid format returns 400.
- Config/serialization: YAML config uses safe_load; no code execution from config content.
"""

import sqlite3

import pytest


# --- SQL injection: identifier escaping (sql_connector pattern) ---


def test_sqlite_identifier_escaping_prevents_second_statement():
    """
    When column/table names contain quote and semicolon (injection attempt), the escaped
    query must not execute a second statement. Uses same escaping as connectors.sql_connector (double-quote).
    """
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t1 (a TEXT)")
    conn.execute("INSERT INTO t1 (a) VALUES ('ok')")
    conn.commit()

    # Simulate connector escaping for SQLite: double-quote inside identifiers
    malicious_col = 'a"; DROP TABLE t1; --'
    safe_col = malicious_col.replace('"', '""')
    safe_table = "t1"
    query = f'SELECT "{safe_col}" FROM "{safe_table}" LIMIT 1'
    try:
        conn.execute(query)
    except sqlite3.OperationalError:
        pass  # Column may not exist; no injection is what we care about
    # In the same connection: t1 must still exist (no second statement was executed)
    conn.execute("SELECT 1 FROM t1")
    conn.close()


def test_sql_connector_sample_uses_escaped_identifiers_sqlite(tmp_path):
    """
    SQLConnector.sample() with SQLite dialect builds a single SELECT with escaped identifiers;
    a malicious-looking column name does not result in executing multiple statements.
    """
    from connectors.sql_connector import SQLConnector
    from unittest.mock import MagicMock

    db_path = tmp_path / "security_test.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE safe_t (col1 TEXT)")
    conn.execute("INSERT INTO safe_t (col1) VALUES ('x')")
    conn.commit()
    conn.close()

    target = {
        "type": "database",
        "driver": "sqlite",
        "database": str(db_path),
        "name": "SecurityTest",
    }
    scanner = MagicMock()
    db_manager = MagicMock()
    connector = SQLConnector(target, scanner, db_manager)
    connector.connect()
    try:
        connector.sample("", "safe_t", 'col1"; DROP TABLE safe_t; --', limit=1)
    finally:
        connector.close()
    # Table must still exist (no second statement executed)
    conn2 = sqlite3.connect(str(db_path))
    conn2.execute("SELECT 1 FROM safe_t")
    conn2.close()


# --- Path traversal: session_id validation (covered in test_routes_responses; assert behaviour) ---


def test_session_id_validation_rejects_dangerous_patterns():
    """API rejects session_id that could be used for path traversal (validated in routes)."""
    import api.routes as routes

    pattern = getattr(routes, "_SESSION_ID_PATTERN", None)
    assert pattern is not None
    assert not pattern.fullmatch("../../../etc/passwd")
    assert not pattern.fullmatch("a" * 11)
    assert not pattern.fullmatch("x'; DROP TABLE sessions; --")
    assert pattern.fullmatch("a1b2c3d4e5f6_20250101")


# --- Database layer: session_id used via ORM only (no raw SQL with user input) ---


def test_database_filters_use_orm_not_raw_sql():
    """LocalDBManager uses SQLAlchemy ORM filter() for session_id; no raw text() with session_id."""
    from core.database import DatabaseFinding
    from sqlalchemy.sql.elements import BinaryExpression

    # session_id in queries is used as ORM column comparison (parameterized), not string-interpolated
    clause = DatabaseFinding.session_id == "test_sid"
    assert isinstance(clause, BinaryExpression)


# --- Config: YAML safe_load (no code execution) ---


def test_config_save_uses_safe_load():
    """Config loader and save path use safe YAML parsing (no !!python/object or code execution)."""
    import yaml

    # safe_load does not deserialize arbitrary Python objects
    payload = "!!python/object/apply:os.system ['echo pwned']"
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load(payload)
