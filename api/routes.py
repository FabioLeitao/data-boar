from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import os
from core.engine import AuditEngine
from utils.logger import setup_live_logger

app = FastAPI(title="LGPD/GDPR Audit API", version="1.0.0")
logger = setup_live_logger()

# Instância global do motor (será configurada no startup)
audit_engine = None

@app.on_event("startup")
async def startup_event():
    global audit_engine
    # Carrega a configuração padrão ou via variável de ambiente
    import yaml
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    audit_engine = AuditEngine(config)

@app.post("/audit/start")
async def start_audit(background_tasks: BackgroundTasks):
    """Inicia a varredura completa em segundo plano."""
    if audit_engine.is_running:
        return {"status": "error", "message": "Uma auditoria já está em curso."}
    
    background_tasks.add_task(audit_engine.start_audit)
    return {"status": "success", "message": "Auditoria iniciada em background."}

@app.get("/audit/status")
async def get_status():
    """Retorna o progresso atual e se há violações detectadas."""
    return {
        "running": audit_engine.is_running,
        "last_session": audit_engine.db_manager.current_session_id,
        "findings_count": audit_engine.get_current_findings_count()
    }

@app.get("/audit/report")
async def download_report():
    """Gera e permite o download do último relatório Excel."""
    report_path = audit_engine.generate_final_reports()
    if os.path.exists(report_path):
        return FileResponse(path=report_path, filename=report_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    raise HTTPException(status_code=404, detail="Relatório ainda não gerado.")
