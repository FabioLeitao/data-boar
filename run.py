#!/usr/bin/env python3
"""
Legacy entry point: thin wrapper around main.py flow.
Uses config.loader and core.engine.AuditEngine; for --web uses api.routes.app on port 8088.
Prefer: python main.py --config config.yaml [--web] [--port 8088]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.loader import load_config
from core.engine import AuditEngine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml", help="Path to YAML or JSON config")
    parser.add_argument("--web", action="store_true", help="Start REST API (port 8088)")
    parser.add_argument("--port", type=int, default=8088, help="API port when --web")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError:
        example = {"targets": [{"name": "Local_Files", "type": "filesystem", "path": "./", "recursive": True}]}
        import yaml
        with open(args.config, "w") as f:
            yaml.dump(example, f)
        config = load_config(args.config)
    except Exception as e:
        print(f"Config error: {e}")
        sys.exit(1)

    engine = AuditEngine(config)

    if args.web:
        import uvicorn
        from api.routes import app
        port = config.get("api", {}).get("port", args.port)
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        session_id = engine.start_audit()
        print(f"Scan session: {session_id}")
        report_path = engine.generate_final_reports(session_id)
        if report_path:
            print(f"Report written: {report_path}")
        else:
            print("No findings to report.")


if __name__ == "__main__":
    main()
