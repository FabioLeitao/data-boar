"""
AuditEngine: orchestrates targets from config via connector registry; uses LocalDBManager and DataScanner.
Supports sequential or parallel (max_workers) scan; start_audit(), generate_final_reports(session_id).
Exposes db_manager, is_running, get_current_findings_count() for API.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

# Import connectors so they register themselves
import connectors.sql_connector  # noqa: F401
import connectors.filesystem_connector  # noqa: F401
try:
    import connectors.mongodb_connector  # noqa: F401
except ImportError:
    pass
try:
    import connectors.redis_connector  # noqa: F401
except ImportError:
    pass

from core.connector_registry import connector_for_target
from core.database import LocalDBManager
from core.scanner import DataScanner
from core.session import new_session_id


class AuditEngine:
    def __init__(self, config: dict[str, Any], db_path: str | None = None):
        self.config = config
        self.db_path = db_path or config.get("sqlite_path", "audit_results.db")
        self.db_manager = LocalDBManager(self.db_path)
        self.scanner = DataScanner(
            regex_overrides_path=config.get("regex_overrides_file") or None,
            ml_patterns_path=config.get("ml_patterns_file") or None,
        )
        self._is_running = False
        self._last_report_path: str | None = None
        self._max_workers = int(config.get("scan", {}).get("max_workers", 1))
        self._extensions = config.get("file_scan", {}).get("extensions", [])

    @property
    def is_running(self) -> bool:
        return self._is_running

    def get_current_findings_count(self) -> int:
        return self.db_manager.get_current_findings_count()

    def start_audit(self) -> str:
        """
        Run audit for all targets (sequential or parallel). Returns session_id (UUID + timestamp).
        """
        session_id = new_session_id()
        self.db_manager.set_current_session_id(session_id)
        self.db_manager.create_session_record(session_id)
        self._run_audit_targets()
        return session_id

    def _run_audit_targets(self) -> None:
        """Run all targets; caller must set session_id and create_session_record before."""
        self._is_running = True
        session_id = self.db_manager.current_session_id
        targets = self.config.get("targets", [])
        try:
            if self._max_workers <= 1:
                for target in targets:
                    self._run_target(target)
            else:
                with ThreadPoolExecutor(max_workers=min(self._max_workers, len(targets) or 1)) as ex:
                    futures = {ex.submit(self._run_target, t): t for t in targets}
                    for fut in as_completed(futures):
                        try:
                            fut.result()
                        except Exception:
                            pass
        finally:
            self._is_running = False
            self.db_manager.finish_session(session_id, "completed")

    def _run_target(self, target: dict[str, Any]) -> None:
        """Run one target: resolve connector, instantiate, run()."""
        resolved = connector_for_target(target)
        if not resolved:
            self.db_manager.save_failure(
                target.get("name", "unknown"),
                "error",
                "Unsupported target type or driver",
            )
            return
        connector_class, _ = resolved
        if target.get("type") == "filesystem":
            ext = self.config.get("file_scan", {}).get("extensions")
            if ext is not None:
                connector = connector_class(target, self.scanner, self.db_manager, extensions=ext)
            else:
                connector = connector_class(target, self.scanner, self.db_manager)
        else:
            connector = connector_class(target, self.scanner, self.db_manager)
        try:
            connector.run()
        except Exception as e:
            self.db_manager.save_failure(target.get("name", "unknown"), "error", str(e))

    def generate_final_reports(self, session_id: str | None = None) -> str | None:
        """
        Build Excel + heatmap from SQLite for session_id (or current). Return report file path or None.
        """
        from report.generator import generate_report
        sid = session_id or self.db_manager.current_session_id
        if not sid:
            return None
        out_dir = self.config.get("report", {}).get("output_dir", ".")
        path = generate_report(self.db_manager, sid, output_dir=out_dir)
        if path:
            self._last_report_path = path
        return path

    def get_last_report_path(self) -> str | None:
        return self._last_report_path
