"""
SQL connector: connect via SQLAlchemy, discover schemas/tables/columns, sample rows (no raw storage),
run detector, save_finding. Supports PostgreSQL, MySQL, MariaDB, SQLite, MSSQL, Oracle via driver.
"""
from typing import Any, Callable

from sqlalchemy import create_engine, inspect, text

from core.connector_registry import register

# Driver to SQLAlchemy drivername mapping (driver in config may be e.g. postgresql+psycopg2)
DRIVER_MAP = {
    "postgresql": "postgresql+psycopg2",
    "mysql": "mysql+pymysql",
    "mariadb": "mysql+pymysql",
    "sqlite": "sqlite",
    "mssql": "mssql+pyodbc",
    "oracle": "oracle+oracledb",
}

# Oracle system schemas to skip when discovering (credential sees only accessible schemas; skip Oracle-maintained)
ORACLE_SYSTEM_SCHEMAS = frozenset({
    "SYS", "SYSTEM", "OUTLN", "DBSNMP", "DIP", "ORACLE_OCM", "APPQOSSYS", "WMSYS",
    "EXFSYS", "CTXSYS", "XDB", "ANONYMOUS", "MDSYS", "OLAPSYS", "ORDSYS", "ORDDATA",
    "SI_INFORMTN_SCHEMA", "LBACSYS", "DVF", "DVSYS", "GSMADMIN_INTERNAL", "OJVMSYS",
    "GSMCATUSER", "GSMUSER", "MDDATA", "REMOTE_SCHEDULER_AGENT", "DBSFWUSER",
})


def _build_url(target: dict[str, Any]) -> str:
    """Build SQLAlchemy URL from target config."""
    driver = (target.get("driver") or "postgresql").split("+")[0].lower()
    drivername = DRIVER_MAP.get(driver, f"{driver}")
    # Allow full URL override
    if target.get("url"):
        return target["url"]
    if driver == "sqlite":
        return f"sqlite:///{target.get('database', 'audit.db')}"
    user = target.get("user", "")
    password = target.get("pass", target.get("password", ""))
    host = target.get("host", "localhost")
    port = target.get("port", 5432)
    database = target.get("database", "")
    if "oracle" in drivername:
        return f"{drivername}://{user}:{password}@{host}:{port}/?service_name={database}"
    return f"{drivername}://{user}:{password}@{host}:{port}/{database}"


class SQLConnector:
    """
    Connect to a SQL database, discover tables/columns, sample content, run sensitivity detection,
    save findings (metadata only). Implements connect, discover, sample, close.
    """

    def __init__(
        self,
        target_config: dict[str, Any],
        scanner: Any,
        db_manager: Any,
        sample_limit: int = 5,
    ):
        self.config = target_config
        self.scanner = scanner
        self.db_manager = db_manager
        self.sample_limit = sample_limit
        self.engine = None
        self._connection = None

    def connect(self) -> None:
        url = _build_url(self.config)
        self.engine = create_engine(url, pool_pre_ping=True)
        self._connection = self.engine.connect()

    def close(self) -> None:
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            self._connection = None
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def discover(self) -> list[dict[str, Any]]:
        """Return list of {schema, table, columns: [{name, type}]}. For Oracle, skips system schemas."""
        inspector = inspect(self.engine)
        result = []
        dialect = self.engine.dialect.name if self.engine else ""
        schemas = inspector.get_schema_names()
        skip_schemas = {"information_schema", "sys", "pg_catalog", "performance_schema"}
        if dialect == "oracle":
            skip_schemas = ORACLE_SYSTEM_SCHEMAS
        for schema in schemas:
            if schema and (schema.upper() if dialect == "oracle" else schema) in skip_schemas:
                continue
            try:
                for table in inspector.get_table_names(schema=schema):
                    columns = inspector.get_columns(table, schema=schema)
                    result.append({
                        "schema": schema or "",
                        "table": table,
                        "columns": [{"name": c["name"], "type": str(c["type"])} for c in columns],
                    })
            except Exception:
                continue
        # If no schemas (e.g. SQLite), get_table_names() without schema
        if not result and hasattr(inspector, "get_table_names"):
            for table in inspector.get_table_names():
                columns = inspector.get_columns(table)
                result.append({
                    "schema": "",
                    "table": table,
                    "columns": [{"name": c["name"], "type": str(c["type"])} for c in columns],
                })
        return result

    def sample(self, schema: str, table: str, column_name: str) -> str:
        """Fetch up to sample_limit values from column; return concatenated string for detection (not stored)."""
        dialect = self.engine.dialect.name if self.engine else ""
        # Escape identifier per dialect (simple: avoid injection by using column/table from discover)
        safe_col = column_name.replace('"', '""')
        safe_table = table.replace('"', '""')
        try:
            if dialect == "sqlite":
                q = text(f'SELECT "{safe_col}" FROM "{safe_table}" LIMIT {self.sample_limit}')
            elif dialect == "mysql":
                t = f'`{schema}`.`{safe_table}`' if schema else f'`{safe_table}`'
                q = text(f'SELECT `{safe_col}` FROM {t} LIMIT {self.sample_limit}')
            elif dialect == "oracle":
                # Oracle: quoted identifiers; use ROWNUM for limit (no LIMIT)
                t = f'"{schema}"."{safe_table}"' if schema else f'"{safe_table}"'
                q = text(
                    f'SELECT "{safe_col}" FROM {t} WHERE ROWNUM <= :lim'
                ).bindparams(lim=self.sample_limit)
            else:
                t = f'"{schema}"."{safe_table}"' if schema else f'"{safe_table}"'
                q = text(f'SELECT "{safe_col}" FROM {t} LIMIT {self.sample_limit}')
            rows = self._connection.execute(q).fetchall()
            parts = [str(r[0])[:200] for r in rows if r[0] is not None]
            return " ".join(parts)
        except Exception:
            return ""

    def run(self) -> None:
        """Connect, discover, sample each column, detect, save_finding; on error save_failure."""
        target_name = self.config.get("name", "database")
        server_ip = self.config.get("host", "localhost")
        try:
            self.connect()
        except Exception as e:
            self.db_manager.save_failure(target_name, "unreachable", str(e))
            return
        try:
            from utils.logger import log_connection
            log_connection(target_name, "database", server_ip or "local")
            engine_name = self.engine.dialect.name if self.engine else "sql"
            for item in self.discover():
                schema = item["schema"]
                table = item["table"]
                for col in item["columns"]:
                    cname = col["name"]
                    ctype = col["type"]
                    sample = self.sample(schema, table, cname)
                    res = self.scanner.scan_column(cname, sample)
                    if res["sensitivity_level"] == "LOW":
                        continue
                    self.db_manager.save_finding(
                        source_type="database",
                        target_name=target_name,
                        server_ip=server_ip,
                        engine_details=engine_name,
                        schema_name=schema,
                        table_name=table,
                        column_name=cname,
                        data_type=ctype,
                        sensitivity_level=res["sensitivity_level"],
                        pattern_detected=res["pattern_detected"],
                        norm_tag=res.get("norm_tag", ""),
                        ml_confidence=res.get("ml_confidence", 0),
                    )
                    try:
                        from utils.logger import log_finding
                        log_finding("database", target_name, f"{schema}.{table}.{cname}", res["sensitivity_level"], res["pattern_detected"])
                    except Exception:
                        pass
        except Exception as e:
            self.db_manager.save_failure(target_name, "error", str(e))
        finally:
            self.close()


# Register for common SQL engines
for _t in ("postgresql", "mysql", "mariadb", "sqlite", "mssql", "oracle"):
    register(_t, SQLConnector, ["name", "type"])
