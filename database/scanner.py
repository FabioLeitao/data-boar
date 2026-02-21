from sqlalchemy import inspect
from typing import List, Dict

def scan_database_tables(engine, db_name: str) -> List[Dict]:
    """Escaneia tabelas e colunas de um banco de dados."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    results = []

    for table in tables:
        table_info = inspector.get_table_info(table)
        columns = inspector.get_columns(table)
        results.append({
            "table": table,
            "columns": [{"name": col["name"], "type": col["type"]} for col in columns],
            "metadata": {"db": db_name, "ip": config["host"]}
        })
    return results

