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
    parser = argparse.ArgumentParser(
        description=(
            "LGPD/GDPR/CCPA data audit tool. "
            "Loads a YAML/JSON config, scans configured databases/filesystems/APIs, "
            "stores findings in SQLite and generates an Excel report with heatmaps. "
            "Can run once from the CLI or start a REST API dashboard."
        ),
        epilog=(
            "Configuration:\n"
            "  - Main config file (YAML or JSON) defines targets (databases, filesystems, APIs, shares),\n"
            "    detection options and report settings. Default is 'config.yaml' in the current directory.\n"
            "  - See docs/USAGE.md for a full schema and examples.\n"
            "\n"
            "CLI examples:\n"
            "  # One-shot audit with the default config.yaml\n"
            "  python main.py --config config.yaml\n"
            "\n"
            "  # One-shot audit tagging tenant/customer and technician/operator\n"
            "  python main.py --config config.yaml --tenant \"ACME Corp\" --technician \"Alice\"\n"
            "\n"
            "  # Wipe all collected data and generated reports (dangerous, see SECURITY.md)\n"
            "  python main.py --config config.yaml --reset-data\n"
            "\n"
            "Web/API examples:\n"
            "  # Start REST API using port from config.api.port or 8088 by default\n"
            "  python main.py --config config.yaml --web\n"
            "\n"
            "  # Start REST API explicitly on port 9090 (overrides config.api.port)\n"
            "  python main.py --config config.yaml --web --port 9090\n"
            "\n"
            "Once a one-shot scan finishes, an Excel report and heatmap PNG are written under\n"
            "the configured report.output_dir (default: current directory). When the API is\n"
            "running, you can navigate to the documented endpoints (see README.md) to trigger\n"
            "scans, list sessions and download the latest reports through the browser."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help=(
            "Path to the main YAML or JSON configuration file. "
            "Defines targets (databases, filesystems, APIs/shares), detection settings and report.output_dir. "
            "Default: config.yaml in the current working directory."
        ),
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help=(
            "Start the REST API/dashboard instead of running a single audit. "
            "Uses api.port from the config when present, otherwise falls back to --port (default 8088)."
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8088,
        help=(
            "API port when --web is enabled. "
            "If api.port is set in the config file it takes precedence, unless you explicitly pass --port here. "
            "Default: 8088."
        ),
    )
    parser.add_argument(
        "--reset-data",
        action="store_true",
        help=(
            "DANGER: wipe all scan sessions, findings and failures from the SQLite database, "
            "delete generated Excel reports and heatmap PNGs under report.output_dir, "
            "and record an immutable data_wipe_log entry with the reason. "
            "Intended for lab/demo environments; review SECURITY.md before using in production."
        ),
    )
    parser.add_argument(
        "--tenant",
        default=None,
        help=(
            "Optional customer/tenant name for this scan. "
            "Stored in the session metadata and included in the Excel report header for traceability."
        ),
    )
    parser.add_argument(
        "--technician",
        default=None,
        help=(
            "Optional name of the technician/operator responsible for this scan. "
            "Also stored in session metadata and shown in the report header."
        ),
    )
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
        # Require explicit confirmation: no undo, no going back.
        print()
        print("*** WIPE ALL GATHERED DATA ***")
        print()
        print("This will permanently:")
        print("  - Remove all scan sessions, findings and failures from the SQLite database")
        print("  - Delete all generated Excel reports and heatmap PNGs under report.output_dir")
        print()
        print("There is NO going back after this step. There is NO undo button.")
        print("Only a log entry in the database will record that a wipe was performed.")
        print()
        try:
            answer = input("Type 'yes' to confirm and proceed, or anything else to abort: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = ""
        if answer != "yes":
            print("Aborted. No data was wiped.")
            return
        # Wipe DB contents and generated artifacts, but leave an immutable audit entry of the wipe itself.
        reason = f"CLI --reset-data invoked using config {args.config}"
        engine.db_manager.wipe_all_data(reason)
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
