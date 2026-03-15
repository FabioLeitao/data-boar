"""
SQL connector: connect via SQLAlchemy, discover schemas/tables/columns, sample rows (no raw storage),
run detector, save_finding. Supports PostgreSQL, MySQL, MariaDB, SQLite, MSSQL, Oracle via driver.
"""
from collections.abc import Set
from typing import Any
from urllib.parse import quote

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

_DEFAULT_SKIP_SCHEMAS = {"information_schema", "sys", "pg_catalog", "performance_schema"}


def _get_skip_schemas(dialect: str) -> Set[str]:
    """Return the set of schema names to skip when discovering (dialect-specific)."""
    return ORACLE_SYSTEM_SCHEMAS if dialect == "oracle" else _DEFAULT_SKIP_SCHEMAS


def _should_skip_schema(schema: str | None, dialect: str, skip_schemas: Set[str]) -> bool:
    """True if schema should be skipped (empty or in skip_schemas)."""
    if not schema:
        return True
    key = schema.upper() if dialect == "oracle" else schema
    return key in skip_schemas


def _tables_from_schema(inspector: Any, schema: str) -> list[dict[str, Any]]:
    """Return list of {schema, table, columns} for the given schema; empty list on error."""
    out = []
    try:
        for table in inspector.get_table_names(schema=schema):
            columns = inspector.get_columns(table, schema=schema)
            out.append({
                "schema": schema or "",
                "table": table,
                "columns": [{"name": c["name"], "type": str(c["type"])} for c in columns],
            })
    except Exception:
        pass
    return out


def _discover_fallback_no_schemas(inspector: Any) -> list[dict[str, Any]]:
    """When no schemas (e.g. SQLite), get tables without schema."""
    out = []
    if not hasattr(inspector, "get_table_names"):
        return out
    try:
        for table in inspector.get_table_names():
            columns = inspector.get_columns(table)
            out.append({
                "schema": "",
                "table": table,
                "columns": [{"name": c["name"], "type": str(c["type"])} for c in columns],
            })
    except Exception:
        pass
    return out


def _quote_userinfo(value: str) -> str:
    """URL-encode user or password for use in connection URL userinfo. Prevents special chars (@, :, /, #) from breaking URL parsing."""
    if not value:
        return ""
    return quote(str(value), safe="")


def _build_url(target: dict[str, Any]) -> str:
    """Build SQLAlchemy URL from target config. User and password are URL-encoded to avoid injection or misparsing when they contain @, :, /, #."""
    driver = (target.get("driver") or "postgresql").split("+")[0].lower()
    drivername = DRIVER_MAP.get(driver, f"{driver}")
    # Allow full URL override
    if target.get("url"):
        return target["url"]
    if driver == "sqlite":
        return f"sqlite:///{target.get('database', 'audit.db')}"
    user = _quote_userinfo(target.get("user", ""))
    password = _quote_userinfo(target.get("pass", target.get("password", "")))
    host = target.get("host", "localhost")
    port = target.get("port", 5432)
    database = target.get("database", "")
    if "oracle" in drivername:
        return f"{drivername}://{user}:{password}@{host}:{port}/?service_name={database}"
    return f"{drivername}://{user}:{password}@{host}:{port}/{database}"


def _connect_args_from_target(target: dict[str, Any]) -> dict[str, Any]:
    """
    Build SQLAlchemy connect_args from target timeouts (config loader merges global + per-target).
    Uses connect_timeout_seconds for connect; read_timeout_seconds for statement_timeout (PostgreSQL)
    or SQLite lock timeout.
    """
    connect_s = int(target.get("connect_timeout_seconds", 25))
    read_s = int(target.get("read_timeout_seconds", 90))
    driver = (target.get("driver") or "postgresql").split("+")[0].lower()
    connect_s = max(1, connect_s)
    read_s = max(1, read_s)
    if driver == "sqlite":
        return {"timeout": read_s}
    if driver == "postgresql":
        # statement_timeout in PostgreSQL is in milliseconds
        return {"connect_timeout": connect_s, "options": f"-c statement_timeout={read_s * 1000}"}
    if driver in ("mysql", "mariadb"):
        return {"connect_timeout": connect_s}
    # mssql, oracle, others: pass connect_timeout when driver supports it
    return {"connect_timeout": connect_s}


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
        detection_config: dict[str, Any] | None = None,
    ):
        self.config = target_config
        self.scanner = scanner
        self.db_manager = db_manager
        self.sample_limit = sample_limit
        self.detection_config = detection_config or {}
        self.engine = None
        self._connection = None

    def connect(self) -> None:
        url = _build_url(self.config)
        connect_args = _connect_args_from_target(self.config)
        self.engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)
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
        dialect = self.engine.dialect.name if self.engine else ""
        skip_schemas = _get_skip_schemas(dialect)
        result = []
        for schema in inspector.get_schema_names():
            if _should_skip_schema(schema, dialect, skip_schemas):
                continue
            result.extend(_tables_from_schema(inspector, schema))
        if not result:
            result = _discover_fallback_no_schemas(inspector)
        return result

    def _process_one_finding(
        self,
        target_name: str,
        server_ip: str,
        engine_name: str,
        schema: str,
        table: str,
        cname: str,
        ctype: str,
    ) -> None:
        """Sample column, run detection, optionally full-scan for minor; save finding and log."""
        sample = self.sample(schema, table, cname)
        res = self.scanner.scan_column(cname, sample)
        if res["sensitivity_level"] == "LOW":
            return
        norm_tag = res.get("norm_tag", "")
        if (
            "DOB_POSSIBLE_MINOR" in (res.get("pattern_detected") or "")
            and self.detection_config.get("minor_full_scan")
        ):
            full_scan_limit = self.detection_config.get("minor_full_scan_limit", 100)
            full_sample = self.sample(schema, table, cname, limit=full_scan_limit)
            full_res = self.scanner.scan_column(cname, full_sample)
            if "DOB_POSSIBLE_MINOR" in (full_res.get("pattern_detected") or ""):
                res = full_res
                suffix = " (full-scan confirmed)"
                norm_tag = (norm_tag or "").rstrip() + suffix if norm_tag else suffix.lstrip()
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
            norm_tag=norm_tag,
            ml_confidence=res.get("ml_confidence", 0),
        )
        try:
            from utils.logger import log_finding
            log_finding("database", target_name, f"{schema}.{table}.{cname}", res["sensitivity_level"], res["pattern_detected"])
        except Exception:
            pass

    def sample(self, schema: str, table: str, column_name: str, limit: int | None = None) -> str:
        """Fetch up to limit (or sample_limit) values from column; return concatenated string for detection (not stored)."""
        use_limit = limit if limit is not None else self.sample_limit
        dialect = self.engine.dialect.name if self.engine else ""
        # Escape identifier per dialect to prevent SQL injection (identifiers come from discover(), not user input).
        # Double-quote for SQLite/Postgres/Oracle; backtick for MySQL.
        safe_col = column_name.replace('"', '""')
        safe_table = table.replace('"', '""')
        safe_schema = (schema or "").replace('"', '""')
        try:
            if dialect == "sqlite":
                q = text(f'SELECT "{safe_col}" FROM "{safe_table}" LIMIT {use_limit}')
            elif dialect == "mysql":
                # MySQL uses backticks; escape backtick inside identifiers to prevent injection.
                def _bk(s: str) -> str:
                    return s.replace("`", "``")
                t = f'`{_bk(safe_schema)}`.`{_bk(safe_table)}`' if schema else f'`{_bk(safe_table)}`'
                q = text(f'SELECT `{_bk(safe_col)}` FROM {t} LIMIT {use_limit}')
            elif dialect == "oracle":
                # Oracle: quoted identifiers; use ROWNUM for limit (no LIMIT)
                t = f'"{safe_schema}"."{safe_table}"' if schema else f'"{safe_table}"'
                q = text(
                    f'SELECT "{safe_col}" FROM {t} WHERE ROWNUM <= :lim'
                ).bindparams(lim=use_limit)
            else:
                t = f'"{safe_schema}"."{safe_table}"' if schema else f'"{safe_table}"'
                q = text(f'SELECT "{safe_col}" FROM {t} LIMIT {use_limit}')
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
                    self._process_one_finding(
                        target_name, server_ip, engine_name,
                        schema, table, col["name"], col["type"],
                    )
        except Exception as e:
            self.db_manager.save_failure(target_name, "error", str(e))
        finally:
            self.close()


# Register for common SQL engines
for _t in ("postgresql", "mysql", "mariadb", "sqlite", "mssql", "oracle"):
    register(_t, SQLConnector, ["name", "type"])
