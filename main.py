#!/usr/bin/env python3
"""
CLI entry point: load config (YAML/JSON), run audit and report (optionally tagged with tenant/customer and technician/operator), or start API (--web) on --port (default 8088).
"""
import argparse
import sys
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.loader import load_config
from core.engine import AuditEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="LGPD/GDPR/CCPA data audit: scan databases and filesystems.")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML or JSON config")
    parser.add_argument("--web", action="store_true", help="Start REST API instead of one-shot audit")
    parser.add_argument("--port", type=int, default=8088, help="API port when --web (default 8088)")
    parser.add_argument(
        "--reset-data",
        action="store_true",
        help="Dangerous: wipe all scan sessions and findings, delete generated reports/heatmaps, and log the wipe in SQLite",
    )
    parser.add_argument("--tenant", default=None, help="Customer/tenant name for this scan (stored in session metadata)")
    parser.add_argument("--technician", default=None, help="Name of the technician/operator responsible for this scan")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Config not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Config error: {e}")
        sys.exit(1)

    if args.web and not args.reset_data:
        import uvicorn
        from api.routes import app
        port = config.get("api", {}).get("port", args.port)
        uvicorn.run(app, host="0.0.0.0", port=port)
        return

    engine = AuditEngine(config)

    if args.reset_data:
        # Wipe DB contents and generated artifacts, but leave an immutable audit entry of the wipe itself.
        reason = f"CLI --reset-data invoked using config {args.config}"
        engine.db_manager.wipe_all_data(reason)
        from pathlib import Path

        out_dir = config.get("report", {}).get("output_dir", ".")
        out_path = Path(out_dir)
        # Best-effort cleanup of reports and heatmaps; ignore missing files.
        for pattern in ("Relatorio_Auditoria_*.xlsx", "heatmap_*.png"):
            for p in out_path.glob(pattern):
                try:
                    p.unlink()
                except OSError:
                    pass
        print("All scan sessions, findings and failures were wiped from SQLite.")
        print("Existing Excel reports and heatmap PNGs under report.output_dir were deleted where possible.")
        print("An audit entry was recorded in the data_wipe_log table for transparency.")
        return

    tenant = (args.tenant or "").strip() or None
    technician = (args.technician or "").strip() or None
    session_id = engine.start_audit(tenant_name=tenant, technician_name=technician)
    print(f"Scan session: {session_id}")
    report_path = engine.generate_final_reports(session_id)
    if report_path:
        print(f"Report written: {report_path}")
    else:
        print("No findings to report.")


if __name__ == "__main__":
    main()
