"""
Single SQLite schema for audit results: sessions, database_findings, filesystem_findings, scan_failures.
LocalDBManager: save_finding(source_type, **kwargs), save_failure, get_findings, list_sessions.
Session id comes from core.session (UUID + timestamp); set via set_current_session_id.
"""
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class ScanSession(Base):
    """One scan run: UUID + timestamp, status."""
    __tablename__ = "scan_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="running")  # running, completed, failed


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
    created_at = Column(DateTime, default=datetime.utcnow)


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
    created_at = Column(DateTime, default=datetime.utcnow)


class ScanFailure(Base):
    """Record of a target that could not be scanned (unreachable, auth, permission)."""
    __tablename__ = "scan_failures"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    target_name = Column(String(100))
    reason = Column(String(50))  # unreachable, auth_failed, permission_denied, error
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LocalDBManager:
    """Single SQLite DB for all audit results; session id set externally (core.session)."""

    def __init__(self, db_path: str = "audit_results.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self._session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self._current_session_id: str | None = None

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
        """List all scan sessions with summary (session_id, started_at, status, counts)."""
        session = self._session_factory()
        try:
            from sqlalchemy import func
            sessions = session.query(ScanSession).order_by(ScanSession.started_at.desc()).all()
            out = []
            for s in sessions:
                db_count = session.query(DatabaseFinding).filter(DatabaseFinding.session_id == s.session_id).count()
                fs_count = session.query(FilesystemFinding).filter(FilesystemFinding.session_id == s.session_id).count()
                out.append({
                    "session_id": s.session_id,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "finished_at": s.finished_at.isoformat() if s.finished_at else None,
                    "status": s.status,
                    "database_findings": db_count,
                    "filesystem_findings": fs_count,
                })
            return out
        finally:
            session.close()

    def create_session_record(self, session_id: str) -> None:
        session = self._session_factory()
        try:
            session.add(ScanSession(session_id=session_id, status="running"))
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
