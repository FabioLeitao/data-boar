"""
Snowflake connector: optional, requires snowflake-connector-python (.[bigdata] extra).
Uses Snowflake's Python connector directly (no SQLAlchemy) to discover tables/columns,
sample rows, run sensitivity detection, and save findings as database metadata.

Target config (type: database, driver: snowflake):

  - name: "Warehouse_LGPD"
    type: database
    driver: snowflake
    account: "xy12345.us-east-1"
    user: "AUDIT_USER"
    pass: "secret"
    database: "COMPLIANCE_DB"
    schema: "PUBLIC"
    warehouse: "AUDIT_WH"
    role: "ANALYST"           # optional
"""
from typing import Any

from core.connector_registry import register

try:
    import snowflake.connector  # type: ignore[import]

    _SNOWFLAKE_AVAILABLE = True
except ImportError:
    _SNOWFLAKE_AVAILABLE = False
    snowflake = None  # type: ignore[assignment]


class SnowflakeConnector:
    """
    Connect to Snowflake via snowflake-connector-python, discover tables/columns, sample
    content, run sensitivity detection, and save findings (metadata only).
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
        self.sample_limit = max(int(sample_limit or 5), 1)
        self._conn = None

    def connect(self) -> None:
        if not _SNOWFLAKE_AVAILABLE:
            raise RuntimeError(
                "snowflake-connector-python is required for Snowflake targets. "
                "Install with: uv pip install -e \".[bigdata]\""
            )
        cfg = self.config
        user = cfg.get("user") or cfg.get("username", "")
        password = cfg.get("pass") or cfg.get("password", "")
        account = cfg.get("account", "")
        warehouse = cfg.get("warehouse")
        database = cfg.get("database")
        schema = cfg.get("schema")
        role = cfg.get("role")
        params: dict[str, Any] = {
            "user": user,
            "password": password,
            "account": account,
        }
        if warehouse:
            params["warehouse"] = warehouse
        if database:
            params["database"] = database
        if schema:
            params["schema"] = schema
        if role:
            params["role"] = role
        self._conn = snowflake.connector.connect(**params)  # type: ignore[operator]

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _execute(self, sql: str, params: tuple[Any, ...] | None = None) -> list[tuple]:
        if self._conn is None:
            return []
        cur = self._conn.cursor()
        try:
            cur.execute(sql, params or ())
            return cur.fetchall()
        finally:
            try:
                cur.close()
            except Exception:
                pass

    def _list_tables(self) -> list[dict[str, str]]:
        """
        Return list of {schema, table} for base tables in the current database.
        """
        rows = self._execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name
            """
        )
        out: list[dict[str, str]] = []
        for schema, table in rows:
            out.append({"schema": str(schema or ""), "table": str(table or "")})
        return out

    def _get_columns(self, schema: str, table: str) -> list[dict[str, str]]:
        """
        Return list of {name, type} for columns in the given table.
        """
        rows = self._execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
            """,
            (schema, table),
        )
        out: list[dict[str, str]] = []
        for name, dtype in rows:
            out.append({"name": str(name or ""), "type": str(dtype or "")})
        return out

    def _sample_column(self, schema: str, table: str, column: str) -> str:
        """
        Fetch up to sample_limit values from column; return concatenated string for detection.
        Does not persist any raw content.
        """
        if self._conn is None:
            return ""
        # Simple identifier quoting; names come from information_schema, not user input.
        def _q(identifier: str) -> str:
            return '"' + identifier.replace('"', '""') + '"'

        full_table = f"{_q(schema)}.{_q(table)}" if schema else _q(table)
        col = _q(column)
        sql = f"SELECT {col} FROM {full_table} LIMIT {self.sample_limit}"
        cur = self._conn.cursor()
        parts: list[str] = []
        try:
            cur.execute(sql)
            for row in cur.fetchmany(self.sample_limit):
                if row and row[0] is not None:
                    parts.append(str(row[0])[:200])
        except Exception:
            return ""
        finally:
            try:
                cur.close()
            except Exception:
                pass
        return " ".join(parts)

    def run(self) -> None:
        target_name = self.config.get("name", "Snowflake")
        account = self.config.get("account", "")
        try:
            self.connect()
        except Exception as e:
            self.db_manager.save_failure(target_name, "unreachable", str(e))
            return
        try:
            try:
                from utils.logger import log_connection

                log_connection(target_name, "database", account or "snowflake")
            except Exception:
                pass
            tables = self._list_tables()
            for t in tables:
                schema = t["schema"]
                table = t["table"]
                columns = self._get_columns(schema, table)
                for col in columns:
                    cname = col["name"]
                    ctype = col["type"]
                    sample = self._sample_column(schema, table, cname)
                    res = self.scanner.scan_column(cname, sample)
                    if res.get("sensitivity_level") == "LOW":
                        continue
                    self.db_manager.save_finding(
                        source_type="database",
                        target_name=target_name,
                        server_ip=account or "snowflake",
                        engine_details="snowflake",
                        schema_name=schema,
                        table_name=table,
                        column_name=cname,
                        data_type=ctype,
                        sensitivity_level=res.get("sensitivity_level", "MEDIUM"),
                        pattern_detected=res.get("pattern_detected", ""),
                        norm_tag=res.get("norm_tag", ""),
                        ml_confidence=res.get("ml_confidence", 0),
                    )
                    try:
                        from utils.logger import log_finding

                        location = f"{schema}.{table}.{cname}" if schema else f"{table}.{cname}"
                        log_finding("database", target_name, location, res.get("sensitivity_level", ""), res.get("pattern_detected", ""))
                    except Exception:
                        pass
        except Exception as e:
            self.db_manager.save_failure(target_name, "error", str(e))
        finally:
            self.close()


if _SNOWFLAKE_AVAILABLE:
    register("snowflake", SnowflakeConnector, ["name", "type", "account", "user", "database", "warehouse"])

