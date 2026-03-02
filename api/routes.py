"""
FastAPI app: POST /scan, POST /start, GET /status, GET /report, GET /list, GET /reports/{session_id}.
On startup load config (config.yaml or CONFIG_PATH) and create AuditEngine.
"""
import os
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse

# Load config and create engine at import time (or on startup event)
_config_path = os.environ.get("CONFIG_PATH", "config.yaml")
if not Path(_config_path).exists():
    _config_path = "config.yaml"
_config = None
_audit_engine = None


def _get_config():
    global _config
    if _config is None:
        from config.loader import load_config
        if Path(_config_path).exists():
            _config = load_config(_config_path)
        else:
            _config = {"targets": [], "sqlite_path": "audit_results.db", "report": {"output_dir": "."}, "api": {"port": 8088}}
    return _config


def _get_engine():
    global _audit_engine
    if _audit_engine is None:
        from core.engine import AuditEngine
        _audit_engine = AuditEngine(_get_config())
    return _audit_engine


app = FastAPI(title="LGPD/GDPR/CCPA Audit API", version="1.0.0")


@app.on_event("startup")
async def startup_event():
    _get_config()
    _get_engine()


@app.post("/scan")
@app.post("/start")
async def start_scan(background_tasks: BackgroundTasks):
    """Start audit in background. Returns session_id."""
    engine = _get_engine()
    if engine.is_running:
        raise HTTPException(status_code=409, detail="Audit already in progress.")
    from core.session import new_session_id
    session_id = new_session_id()
    engine.db_manager.set_current_session_id(session_id)
    engine.db_manager.create_session_record(session_id)
    def run_targets():
        engine._run_audit_targets()
    background_tasks.add_task(run_targets)
    return {"status": "started", "session_id": session_id}


@app.get("/status")
async def get_status():
    """Return running, current_session_id, findings_count."""
    engine = _get_engine()
    return {
        "running": engine.is_running,
        "current_session_id": engine.db_manager.current_session_id,
        "findings_count": engine.get_current_findings_count(),
    }


@app.get("/report")
async def download_report():
    """Download last generated report file (Excel)."""
    engine = _get_engine()
    path = engine.get_last_report_path()
    if not path or not Path(path).exists():
        # Try to generate from last session
        sid = engine.db_manager.current_session_id
        if sid:
            path = engine.generate_final_reports(sid)
        else:
            sessions = engine.db_manager.list_sessions()
            if sessions:
                path = engine.generate_final_reports(sessions[0]["session_id"])
    if path and Path(path).exists():
        return FileResponse(path, filename=Path(path).name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    raise HTTPException(status_code=404, detail="Report not available. Run a scan first.")


@app.get("/list")
@app.get("/reports")
async def list_sessions():
    """List past scan sessions (session_id, timestamp, counts) for report recreation."""
    engine = _get_engine()
    sessions = engine.db_manager.list_sessions()
    return {"sessions": sessions}


@app.get("/reports/{session_id}")
async def download_report_by_session(session_id: str):
    """Regenerate and download Excel report for the given session_id."""
    engine = _get_engine()
    path = engine.generate_final_reports(session_id)
    if path and Path(path).exists():
        return FileResponse(path, filename=Path(path).name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    raise HTTPException(status_code=404, detail=f"No data for session {session_id} or report generation failed.")
