"""
Single SQLite schema for audit results: sessions, database_findings, filesystem_findings, scan_failures.
LocalDBManager: save_finding(source_type, **kwargs), save_failure, get_findings, list_sessions.
Session id comes from core.session (UUID + timestamp); set via set_current_session_id.
"""
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def _utc_now() -> datetime:
    """Timezone-aware UTC now for SQLAlchemy column defaults."""
    return datetime.now(timezone.utc)


class ScanSession(Base):
    """
    One scan run: UUID + timestamp, status.
    Optional tenant_name for customer/tenant attribution and technician_name for operator identification.
    """
    __tablename__ = "scan_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    started_at = Column(DateTime, default=_utc_now)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="running")  # running, completed, failed
    tenant_name = Column(String(255), nullable=True)  # optional customer/tenant for this scan
    technician_name = Column(String(255), nullable=True)  # optional technician/operator for this scan


class DatabaseFinding(Base):
    """A single finding from a database target (metadata only, no raw content)."""
    __tablename__ = "database_findings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    target_name = Column(String(100))
    server_ip = Column(String(50))
    engine_details = Column(String(100))
    schema_name = Column(String(100))
    table_name = Column(String(100))
    column_name = Column(String(100))
    data_type = Column(String(50))
    sensitivity_level = Column(String(20))
    pattern_detected = Column(String(100))
    norm_tag = Column(String(100))  # e.g. LGPD Art. 5, GDPR Art. 4(1)
    ml_confidence = Column(Integer)
    created_at = Column(DateTime, default=_utc_now)


class FilesystemFinding(Base):
    """A single finding from a filesystem target."""
    __tablename__ = "filesystem_findings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    target_name = Column(String(100))
    path = Column(String(512))
    file_name = Column(String(255))
    data_type = Column(String(50))  # extension / format
    sensitivity_level = Column(String(20))
    pattern_detected = Column(String(100))
    norm_tag = Column(String(100))
    ml_confidence = Column(Integer)
    created_at = Column(DateTime, default=_utc_now)


class ScanFailure(Base):
    """Record of a target that could not be scanned (unreachable, auth, permission)."""
    __tablename__ = "scan_failures"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    target_name = Column(String(100))
    reason = Column(String(50))  # unreachable, auth_failed, permission_denied, timeout, error
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utc_now)


def failure_hint(reason: str) -> str:
    """
    Map a failure reason into a human-friendly next step.
    Used in reports and logs to help operators fix issues before re-running.
    """
    r = (reason or "").lower()
    if r == "unreachable":
        return (
            "Target did not respond. Check network connectivity (DNS, VPN, routing, firewall rules) "
            "and that the host/path is reachable from the audit host or container."
        )
    if r in {"auth_failed", "authentication_failed"}:
        return (
            "Authentication failed. Verify username/password, tokens or OAuth client credentials, "
            "and check for account lockouts or IP restrictions."
        )
    if r == "permission_denied":
        return (
            "Permission denied. Grant the scanner read access to this resource (filesystem/share/endpoint) "
            "or run it as a user/service account that already has permission."
        )
    if r == "timeout":
        return (
            "Operation timed out. Check for high latency, overloaded target, or too strict timeouts. "
            "Consider increasing timeout values and re-running during off-peak hours."
        )
    return (
        "Unexpected error. Review the detailed message and audit log, verify the target configuration "
        "(host, port, path, credentials) and test connectivity manually before re-running."
    )


class DataWipeLog(Base):
    """
    Audit log for destructive maintenance operations (e.g. wiping all scan data).
    Rows in this table are preserved when wipe_all_data() is called so that there is a trace
    of when and why previous history was cleared.
    """
    __tablename__ = "data_wipe_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    wiped_at = Column(DateTime, default=_utc_now)
    reason = Column(Text, nullable=False)


class LocalDBManager:
    """Single SQLite DB for all audit results; session id set externally (core.session)."""

    def __init__(self, db_path: str = "audit_results.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self._ensure_tenant_column()
        self._ensure_technician_column()
        self._session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self._current_session_id: str | None = None

    def _ensure_tenant_column(self) -> None:
        """Add tenant_name column to scan_sessions if missing (migration for existing DBs)."""
        with self.engine.connect() as conn:
            r = conn.execute(text("SELECT 1 FROM pragma_table_info('scan_sessions') WHERE name='tenant_name'"))
            if r.fetchone() is None:
                conn.execute(text("ALTER TABLE scan_sessions ADD COLUMN tenant_name VARCHAR(255)"))
                conn.commit()

    def _ensure_technician_column(self) -> None:
        """Add technician_name column to scan_sessions if missing (migration for existing DBs)."""
        with self.engine.connect() as conn:
            r = conn.execute(text("SELECT 1 FROM pragma_table_info('scan_sessions') WHERE name='technician_name'"))
            if r.fetchone() is None:
                conn.execute(text("ALTER TABLE scan_sessions ADD COLUMN technician_name VARCHAR(255)"))
                conn.commit()

    def set_current_session_id(self, session_id: str) -> None:
        self._current_session_id = session_id

    @property
    def current_session_id(self) -> str:
        return self._current_session_id or ""

    def save_finding(self, source_type: str, **kwargs: Any) -> None:
        sid = self._current_session_id
        if not sid:
            return
        session = self._session_factory()
        try:
            if source_type == "database":
                kwargs["session_id"] = sid
                finding = DatabaseFinding(**{k: v for k, v in kwargs.items() if hasattr(DatabaseFinding, k)})
                session.add(finding)
            elif source_type == "filesystem":
                kwargs["session_id"] = sid
                finding = FilesystemFinding(**{k: v for k, v in kwargs.items() if hasattr(FilesystemFinding, k)})
                session.add(finding)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save_failure(self, target_name: str, reason: str, details: str | None = None) -> None:
        sid = self._current_session_id
        if not sid:
            return
        # Best-effort logging: mirror failures into the unified audit log so operators
        # can see which target was skipped and why.
        try:
            from utils.logger import get_logger

            logger = get_logger()
            logger.error(
                "Scan failure: session=%s target=%s reason=%s details=%s",
                sid,
                target_name,
                reason,
                (details or "").strip(),
            )
        except Exception:
            # Logging must not break persistence.
            pass
        session = self._session_factory()
        try:
            session.add(ScanFailure(session_id=sid, target_name=target_name, reason=reason, details=details))
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_findings(self, session_id: str | None = None) -> tuple[list[dict], list[dict], list[dict]]:
        """Return (database_findings, filesystem_findings, failures) for session_id or current."""
        sid = session_id or self._current_session_id
        if not sid:
            return [], [], []
        session = self._session_factory()
        try:
            db_rows = session.query(DatabaseFinding).filter(DatabaseFinding.session_id == sid).all()
            fs_rows = session.query(FilesystemFinding).filter(FilesystemFinding.session_id == sid).all()
            fail_rows = session.query(ScanFailure).filter(ScanFailure.session_id == sid).all()
            def db_to_dict(r): return {c.key: getattr(r, c.key) for c in r.__table__.columns}
            return ([db_to_dict(r) for r in db_rows], [db_to_dict(r) for r in fs_rows], [db_to_dict(r) for r in fail_rows])
        finally:
            session.close()

    def list_sessions(self) -> list[dict]:
        """List all scan sessions with summary (session_id, started_at, status, counts including scan_failures)."""
        session = self._session_factory()
        try:
            sessions = session.query(ScanSession).order_by(ScanSession.started_at.desc()).all()
            out = []
            for s in sessions:
                db_count = session.query(DatabaseFinding).filter(DatabaseFinding.session_id == s.session_id).count()
                fs_count = session.query(FilesystemFinding).filter(FilesystemFinding.session_id == s.session_id).count()
                fail_count = session.query(ScanFailure).filter(ScanFailure.session_id == s.session_id).count()
                out.append({
                    "session_id": s.session_id,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "finished_at": s.finished_at.isoformat() if s.finished_at else None,
                    "status": s.status,
                    "tenant_name": getattr(s, "tenant_name", None),
                    "technician_name": getattr(s, "technician_name", None),
                    "database_findings": db_count,
                    "filesystem_findings": fs_count,
                    "scan_failures": fail_count,
                })
            return out
        finally:
            session.close()

    def get_previous_session(self, session_id: str) -> dict | None:
        """
        Return the session immediately before the given one (by started_at desc), for trend comparison.
        Returns dict with session_id, started_at, database_findings, filesystem_findings, scan_failures, or None.
        """
        sessions = self.list_sessions()
        for i, s in enumerate(sessions):
            if s["session_id"] == session_id and i + 1 < len(sessions):
                return sessions[i + 1]
        return None

    def create_session_record(
        self,
        session_id: str,
        tenant_name: str | None = None,
        technician_name: str | None = None,
    ) -> None:
        """Create a scan_sessions row. Optional tenant_name and technician_name metadata."""
        session = self._session_factory()
        try:
            session.add(
                ScanSession(
                    session_id=session_id,
                    status="running",
                    tenant_name=(tenant_name or None),
                    technician_name=(technician_name or None),
                )
            )
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_session_tenant(self, session_id: str, tenant_name: str | None) -> None:
        """Set or clear tenant_name for an existing session."""
        session = self._session_factory()
        try:
            rec = session.query(ScanSession).filter(ScanSession.session_id == session_id).first()
            if rec:
                rec.tenant_name = tenant_name or None
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_session_technician(self, session_id: str, technician_name: str | None) -> None:
        """Set or clear technician_name for an existing session."""
        session = self._session_factory()
        try:
            rec = session.query(ScanSession).filter(ScanSession.session_id == session_id).first()
            if rec:
                rec.technician_name = technician_name or None
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def finish_session(self, session_id: str, status: str = "completed") -> None:
        session = self._session_factory()
        try:
            rec = session.query(ScanSession).filter(ScanSession.session_id == session_id).first()
            if rec:
                rec.finished_at = datetime.now(timezone.utc)
                rec.status = status
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_current_findings_count(self) -> int:
        sid = self._current_session_id
        if not sid:
            return 0
        session = self._session_factory()
        try:
            db_c = session.query(DatabaseFinding).filter(DatabaseFinding.session_id == sid).count()
            fs_c = session.query(FilesystemFinding).filter(FilesystemFinding.session_id == sid).count()
            return db_c + fs_c
        finally:
            session.close()

    def wipe_all_data(self, reason: str) -> None:
        """
        Delete all scan sessions and findings from the SQLite database, but keep an audit entry
        in data_wipe_log so there is a record of when and why the wipe happened.
        Intended to be called from maintenance/CLI tooling (e.g. --reset-data).
        """
        session = self._session_factory()
        try:
            # Delete findings and failures for all sessions
            session.query(DatabaseFinding).delete(synchronize_session=False)
            session.query(FilesystemFinding).delete(synchronize_session=False)
            session.query(ScanFailure).delete(synchronize_session=False)
            # Delete all scan session rows
            session.query(ScanSession).delete(synchronize_session=False)
            # Record the wipe event itself
            session.add(DataWipeLog(reason=reason))
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def dispose(self) -> None:
        """Release engine connections. Call when done with the manager (e.g. in tests)."""
        self.engine.dispose()
