import pytest
from database.connectors import get_db_connection
from database.scanner import scan_database_tables

def test_scan_database():
    # Mock de configuração
    config = {"host": "localhost", "port": 5432, "user": "test", "password": "test", "database": "test"}
    engine = get_db_connection(config)
    tables = scan_database_tables(engine, "test")
    assert len(tables) > 0

