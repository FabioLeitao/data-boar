#!/usr/bin/env python3
import json
import logging
from typing import List
from database.connectors import get_db_connection
from database.scanner import scan_database_tables
from file_scan.text_extractor import detect_sensitive_data
from report.sqlite_reporter import create_sqlite_report
from logging_custom.logger import setup_logging, notify_violation


def main():
    with open("config/config.json") as f:
        config = json.load(f)

    # Testar conexão com banco de dados
    for db in config["databases"]:
        engine = get_db_connection(db)
        tables = scan_database_tables(engine, db["database"])
        for table in tables:
            logging.info(f"Escaneando tabela: {table['table']}")

    # Escaneamento de arquivos
    for directory in config["file_scan"]["directories"]:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(config["file_scan"]["extensions"]):
                    with open(os.path.join(root, file), "r") as f:
                        data = detect_sensitive_data(f.read())
                        if data:
                            notify_violation(data)
                            create_sqlite_report(data)


if __name__ == "__main__":
    setup_logging({"log_level": "INFO"})
    main()
