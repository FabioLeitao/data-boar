#!/usr/bin/env python3
"""
CLI entry point: load config (YAML/JSON), run audit and report, or start API (--web) on --port (default 8088).
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
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Config not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Config error: {e}")
        sys.exit(1)

    if args.web:
        import uvicorn
        from api.routes import app
        port = config.get("api", {}).get("port", args.port)
        uvicorn.run(app, host="0.0.0.0", port=port)
        return

    engine = AuditEngine(config)
    session_id = engine.start_audit()
    print(f"Scan session: {session_id}")
    report_path = engine.generate_final_reports(session_id)
    if report_path:
        print(f"Report written: {report_path}")
    else:
        print("No findings to report.")


if __name__ == "__main__":
    main()
