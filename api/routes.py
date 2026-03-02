"""
FastAPI app: dashboard (GET /), config (GET/POST /config), reports list (GET /reports).
API: POST /scan and /start (optional tenant/technician tags), GET /status, /report, /list,
GET /reports/{session_id}, POST /scan_database (optional tenant/technician), PATCH /sessions/{session_id}
and /sessions/{session_id}/technician for metadata updates. On startup load config (config.yaml or CONFIG_PATH)
and create a singleton AuditEngine.
"""
import os
from pathlib import Path

import yaml
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

_api_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_api_dir / "templates"))


class DatabaseConfig(BaseModel):
    """Single database target for one-off scan via POST /scan_database."""
    name: str
    host: str
    port: int
    user: str
    password: str
    database: str
    driver: str = "postgresql+psycopg2"
    tenant: str | None = None  # optional customer/tenant name for this scan
    technician: str | None = None  # optional technician/operator name for this scan


class ScanStartBody(BaseModel):
    """Optional body for POST /scan to associate the scan with a tenant/customer and technician/operator."""
    tenant: str | None = None
    technician: str | None = None

# Load config and create engine at import time (or on startup event)
_config_path = os.environ.get("CONFIG_PATH", "config.yaml")
if not Path(_config_path).exists():
    _config_path = "config.yaml"
_config = None
_audit_engine = None


def _get_config_path() -> str:
    """Return path to config file (for dashboard display and save)."""
    return _config_path


def _get_config_raw() -> str:
    """Return raw config file content (YAML) for editing. If file missing, return default YAML."""
    p = Path(_config_path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return _default_config_yaml()


def _default_config_yaml() -> str:
    return """# LGPD Audit configuration
targets: []
file_scan:
  extensions: [.txt, .csv, .pdf, .docx, .xlsx]
  recursive: true
  scan_sqlite_as_db: true
  sample_limit: 5
report:
  output_dir: .
api:
  port: 8088
sqlite_path: audit_results.db
scan:
  max_workers: 1
"""


def _save_config_yaml(yaml_content: str) -> None:
    """Validate and save config file; reset in-memory config and engine so next request reloads."""
    from config.loader import normalize_config
    p = Path(_config_path)
    try:
        data = yaml.safe_load(yaml_content)
        if not isinstance(data, dict):
            raise ValueError("Config must be a YAML object")
        normalize_config(data)
    except Exception as e:
        raise ValueError(f"Invalid YAML or config: {e}") from e
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml_content, encoding="utf-8")
    global _config, _audit_engine
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

app.mount("/static", StaticFiles(directory=str(_api_dir / "static")), name="static")


@app.on_event("startup")
async def startup_event():
    _get_config()
    _get_engine()


@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    """Help and documentation page: quickstart, config example, links to README/USAGE docs."""
    return templates.TemplateResponse(
        request=request,
        name="help.html",
        context={},
    )


def _build_chart_data(sessions: list[dict]) -> list[dict]:
    """
    Build progress chart data: one point per session (oldest first) with total findings and risk score.
    Score formula: min(100, total_findings * 2 + scan_failures * 5). Used for dashboard "Progress over time" chart.
    """
    ordered = list(reversed(sessions))  # chronological order for time axis
    out = []
    for s in ordered:
        total = s["database_findings"] + s["filesystem_findings"]
        score = min(100, total * 2 + s["scan_failures"] * 5)
        started = s.get("started_at") or ""
        # Short label for axis (date only if ISO format)
        label = started[:10] if len(started) >= 10 else started or "—"
        out.append({"label": label, "started_at": started, "total_findings": total, "score": round(score, 1)})
    return out


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard: scan status, discovery stats, progress chart, recent sessions, start scan."""
    engine = _get_engine()
    status = {
        "running": engine.is_running,
        "current_session_id": engine.db_manager.current_session_id,
        "findings_count": engine.get_current_findings_count(),
    }
    sessions = engine.db_manager.list_sessions()
    last_session = sessions[0] if sessions else None
    chart_data = _build_chart_data(sessions)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "status": status,
            "sessions": sessions,
            "last_session": last_session,
            "chart_data": chart_data,
        },
    )


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """Configuration editor (YAML). Query: saved=1 or error=... for feedback after POST."""
    saved = request.query_params.get("saved") == "1"
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        request=request,
        name="config.html",
        context={
            "config_path": _get_config_path(),
            "config_yaml": _get_config_raw(),
            "config_saved": saved,
            "config_save_error": error,
        },
    )


@app.post("/config", response_class=HTMLResponse)
async def config_save(request: Request):
    """Save configuration (form body: yaml=...). Redirects back to GET /config with success or error."""
    form = await request.form()
    yaml_content = form.get("yaml", "")
    if not yaml_content:
        return templates.TemplateResponse(
            request=request,
            name="config.html",
            context={
                "config_path": _get_config_path(),
                "config_yaml": _get_config_raw(),
                "config_saved": False,
                "config_save_error": "No YAML content provided.",
            },
        )
    try:
        _save_config_yaml(yaml_content)
        return RedirectResponse(url="/config?saved=1", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="config.html",
            context={
                "config_path": _get_config_path(),
                "config_yaml": yaml_content,
                "config_saved": False,
                "config_save_error": str(e),
            },
        )


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports list page with download links. Query: sort=date_desc (newest first, default) or sort=date_asc (oldest first)."""
    engine = _get_engine()
    sessions = engine.db_manager.list_sessions()
    sort = (request.query_params.get("sort") or "date_desc").strip().lower()
    if sort == "date_asc":
        sessions = list(reversed(sessions))
        sort = "date_asc"
    else:
        sort = "date_desc"
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={"sessions": sessions, "sort": sort},
    )


@app.post("/scan")
@app.post("/start")
async def start_scan(background_tasks: BackgroundTasks, body: ScanStartBody | None = None):
    """Start audit in background. Optional body.tenant and body.technician to tag the scan. Returns session_id."""
    engine = _get_engine()
    if engine.is_running:
        raise HTTPException(status_code=409, detail="Audit already in progress.")
    from core.session import new_session_id
    session_id = new_session_id()
    tenant = (body.tenant if body else None) or None
    technician = (body.technician if body else None) or None
    if isinstance(tenant, str):
        tenant = tenant.strip() or None
    if isinstance(technician, str):
        technician = technician.strip() or None
    engine.db_manager.set_current_session_id(session_id)
    engine.db_manager.create_session_record(
        session_id,
        tenant_name=tenant,
        technician_name=technician,
    )
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


@app.get("/heatmap")
async def download_heatmap():
    """Download last generated heatmap PNG (sensitivity/risk heatmap for the most recent session)."""
    engine = _get_engine()
    # Try to reuse last report path; if missing, generate from last known session as in /report.
    path = engine.get_last_report_path()
    sid: str | None = None
    if not path or not Path(path).exists():
        sid = engine.db_manager.current_session_id or None
        if not sid:
            sessions = engine.db_manager.list_sessions()
            if sessions:
                sid = sessions[0]["session_id"]
        if not sid:
            raise HTTPException(status_code=404, detail="Heatmap not available. Run a scan first.")
        path = engine.generate_final_reports(sid)
    # At this point we have a report path and can infer session_id if needed
    if not path or not Path(path).exists():
        raise HTTPException(status_code=404, detail="Heatmap not available. Run a scan first.")
    report_path = Path(path)
    if not sid:
        # Recover session prefix from report filename: Relatorio_Auditoria_<session_prefix>.xlsx
        name = report_path.name
        prefix = name.removeprefix("Relatorio_Auditoria_").removesuffix(".xlsx")
        sid = prefix
    out_dir = report_path.parent
    heatmap_path = out_dir / f"heatmap_{sid[:12]}.png"
    if heatmap_path.exists():
        return FileResponse(heatmap_path, filename=heatmap_path.name, media_type="image/png")
    raise HTTPException(status_code=404, detail="Heatmap not available. Run a scan first or ensure the report was generated.")


@app.get("/list")
async def list_sessions_api(sort: str = "date_desc"):
    """List past scan sessions (session_id, timestamp, tenant_name, counts) for report recreation (JSON API). Query: sort=date_desc (newest first, default) or sort=date_asc (oldest first)."""
    engine = _get_engine()
    sessions = engine.db_manager.list_sessions()
    if (sort or "").strip().lower() == "date_asc":
        sessions = list(reversed(sessions))
    return {"sessions": sessions}


class SessionTenantUpdate(BaseModel):
    """Body for PATCH /sessions/{session_id}: set tenant/customer name for a session."""
    tenant: str | None = None


class SessionTechnicianUpdate(BaseModel):
    """Body for PATCH /sessions/{session_id}/technician: set technician/operator name for a session."""
    technician: str | None = None


@app.patch("/sessions/{session_id}")
async def update_session_tenant(session_id: str, body: SessionTenantUpdate):
    """Set or clear the tenant/customer name for an existing scan session."""
    engine = _get_engine()
    sessions = [s for s in engine.db_manager.list_sessions() if s.get("session_id") == session_id]
    if not sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    tenant = (body.tenant or "").strip() or None
    engine.db_manager.update_session_tenant(session_id, tenant)
    return {"session_id": session_id, "tenant": tenant}


@app.patch("/sessions/{session_id}/technician")
async def update_session_technician(session_id: str, body: SessionTechnicianUpdate):
    """Set or clear the technician/operator name for an existing scan session."""
    engine = _get_engine()
    sessions = [s for s in engine.db_manager.list_sessions() if s.get("session_id") == session_id]
    if not sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
    technician = (body.technician or "").strip() or None
    engine.db_manager.update_session_technician(session_id, technician)
    return {"session_id": session_id, "technician": technician}


@app.get("/reports/{session_id}")
async def download_report_by_session(session_id: str):
    """Regenerate and download Excel report for the given session_id."""
    engine = _get_engine()
    path = engine.generate_final_reports(session_id)
    if path and Path(path).exists():
        return FileResponse(path, filename=Path(path).name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    raise HTTPException(status_code=404, detail=f"No data for session {session_id} or report generation failed.")


@app.get("/heatmap/{session_id}")
async def download_heatmap_by_session(session_id: str):
    """Regenerate report (if needed) and download heatmap PNG for the given session_id."""
    engine = _get_engine()
    path = engine.generate_final_reports(session_id)
    if not path or not Path(path).exists():
        raise HTTPException(status_code=404, detail=f"No data for session {session_id} or report generation failed.")
    out_dir = Path(path).parent
    heatmap_path = out_dir / f"heatmap_{session_id[:12]}.png"
    if heatmap_path.exists():
        return FileResponse(heatmap_path, filename=heatmap_path.name, media_type="image/png")
    raise HTTPException(status_code=404, detail=f"Heatmap not available for session {session_id}. Run a scan and ensure findings exist.")


@app.get("/logs")
async def download_latest_log():
    """
    Download the most recent audit_YYYYMMDD.log file from the current working directory.
    This file contains connection and finding logs for recent scan sessions.
    """
    log_dir = Path(".")
    candidates = sorted(log_dir.glob("audit_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise HTTPException(status_code=404, detail="No log files found.")
    latest = candidates[0]
    return FileResponse(latest, filename=latest.name, media_type="text/plain")


@app.get("/logs/{session_id}")
async def download_log_for_session(session_id: str):
    """
    Download the first audit_YYYYMMDD.log file that contains the given session_id.
    This allows linking scan sessions to their corresponding console/audit trace.
    """
    log_dir = Path(".")
    candidates = sorted(log_dir.glob("audit_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise HTTPException(status_code=404, detail="No log files found.")
    for p in candidates:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if session_id in text:
            return FileResponse(p, filename=p.name, media_type="text/plain")
    raise HTTPException(status_code=404, detail=f"No log file contains session_id {session_id}.")


@app.post("/scan_database")
async def scan_database(config: DatabaseConfig, background_tasks: BackgroundTasks):
    """One-off scan of a single database (body: name, host, port, user, password, database, optional driver). Starts in background; returns session_id."""
    engine = _get_engine()
    if engine.is_running:
        raise HTTPException(status_code=409, detail="Audit already in progress.")
    target = {
        "name": config.name,
        "type": "database",
        "driver": config.driver,
        "host": config.host,
        "port": config.port,
        "user": config.user,
        "pass": config.password,
        "database": config.database,
    }
    from core.session import new_session_id
    session_id = new_session_id()
    tenant = (config.tenant or "").strip() or None
    technician = (config.technician or "").strip() or None
    engine.db_manager.set_current_session_id(session_id)
    engine.db_manager.create_session_record(
        session_id,
        tenant_name=tenant,
        technician_name=technician,
    )
    def run_one_target():
        engine._is_running = True
        try:
            engine._run_target(target)
        finally:
            engine._is_running = False
            engine.db_manager.finish_session(session_id, "completed")
    background_tasks.add_task(run_one_target)
    return {"status": "started", "session_id": session_id}
