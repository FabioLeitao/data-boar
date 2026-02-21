import pytest
from scanner.data_scanner import DataScanner
from scanner.db_connector import DBConnector


@pytest.fixture
def mock_db_connector():
    connector = DBConnector()
    connector.connections = {"MockDB": "MockConnection"}
    return connector


def test_scan(mock_db_connector):
    scanner = DataScanner(mock_db_connector)
    scanner.scan()
    assert True  # Simplesmente validar que não há erros
