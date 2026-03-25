#!/usr/bin/env python3
"""
CLI entry point: load config (YAML/JSON), run audit and report (optionally tagged with tenant/customer and technician/operator), or start API (--web) on --host/--port (defaults: loopback, 8088; see resolve_api_host).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.loader import load_config
from core.database import LocalDBManager
from core.engine import AuditEngine
from core.licensing import LicenseBlockedError
from core.runtime_trust import get_runtime_trust_snapshot


def _emit_runtime_trust_info(
    snapshot: dict[str, Any], *, to_stdout: bool = True, to_stderr: bool = True
) -> None:
    info_line = (
        "[INFO] runtime-trust: "
        f"{snapshot['trust_level'].upper()} "
        f"(license_state={snapshot['license_state']}, "
        f"mode={snapshot['license_mode']})"
    )
    if to_stdout:
        print(info_line)
    if to_stderr:
        print(info_line, file=sys.stderr)

    if not snapshot["is_unexpected"]:
        return

    attention_line = (
        "[INFO] runtime-trust attention: "
        "THERE IS SOMETHING DIFFERENT AND UNEXPECTED IN THIS RUNTIME. "
        "Review license/integrity state before trusting scan or report outputs."
    )
    if to_stdout:
        print(attention_line)
    if to_stderr:
        print(attention_line, file=sys.stderr)


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
            '  python main.py --config config.yaml --tenant "ACME Corp" --technician "Alice"\n'
            "\n"
            "  # One-shot with archive scan + content-type detection (this run only)\n"
            "  python main.py --config config.yaml --scan-compressed --content-type-check\n"
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
            "  # Bind API on all interfaces (overrides config api.host and API_HOST; use with care)\n"
            "  python main.py --config config.yaml --web --host 0.0.0.0\n"
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
        "--host",
        default=None,
        metavar="ADDR",
        help=(
            "Bind address when --web is enabled (e.g. 127.0.0.1 or 0.0.0.0). "
            "Takes precedence over api.host in config and over the API_HOST environment variable. "
            "If omitted, resolution follows config api.host, then API_HOST, then safe default 127.0.0.1. "
            "Ignored in one-shot CLI mode."
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
        "--export-audit-trail",
        metavar="PATH",
        nargs="?",
        const="-",
        default=None,
        help=(
            "Export a JSON audit trail from SQLite (data_wipe_log, session summary; "
            "future: integrity anchor). PATH optional: omit or '-' for stdout; "
            "otherwise write to PATH. Does not modify the database. "
            "Incompatible with --web and --reset-data."
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
    parser.add_argument(
        "--scan-compressed",
        action="store_true",
        help=(
            "When set, act as if file_scan.scan_compressed is true for this run: "
            "scan inside supported archives (zip, tar, 7z, etc.). May increase run time and I/O."
        ),
    )
    parser.add_argument(
        "--content-type-check",
        action="store_true",
        dest="content_type_check",
        help=(
            "When set, act as if file_scan.use_content_type is true for this run: "
            "infer file format from magic bytes (first bytes of each file), not only extension—"
            "helps find renamed or cloaked files. Adds extra I/O and CPU per file."
        ),
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Config not found: {e}")
        print("Probable cause: The config file path is wrong or the file was moved.")
        print(
            "What to do: Check the path, use --config to point to your YAML/JSON, or create config.yaml in the current directory."
        )
        sys.exit(1)
    except Exception as e:
        print(f"Config error: {e}")
        print("Probable cause: Invalid YAML/JSON syntax or a required key is missing.")
        print(
            "What to do: Validate your config against docs/USAGE.md; check indentation and quoted strings."
        )
        sys.exit(1)

    if args.scan_compressed:
        config.setdefault("file_scan", {})["scan_compressed"] = True
    if args.content_type_check:
        config.setdefault("file_scan", {})["use_content_type"] = True

    runtime_trust = get_runtime_trust_snapshot(config)

    if args.export_audit_trail is not None:
        # Keep stdout clean for JSON when export destination is stdout.
        _emit_runtime_trust_info(runtime_trust, to_stdout=False, to_stderr=True)
        if args.web:
            print(
                "Cannot combine --export-audit-trail with --web.",
                file=sys.stderr,
            )
            sys.exit(2)
        if args.reset_data:
            print(
                "Cannot combine --export-audit-trail with --reset-data.",
                file=sys.stderr,
            )
            sys.exit(2)
        from core.audit_export import build_audit_trail_payload

        engine = AuditEngine(config)
        try:
            sqlite_path = config.get("sqlite_path", "audit_results.db")
            payload = build_audit_trail_payload(
                engine.db_manager,
                config=config,
                config_path=args.config,
                sqlite_path=sqlite_path,
            )
            body = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
            dest = args.export_audit_trail
            if dest in ("-", None):
                sys.stdout.write(body)
            else:
                Path(dest).write_text(body, encoding="utf-8")
                print(f"Audit trail exported to {dest}", file=sys.stderr)
        finally:
            engine.db_manager.dispose()
        return

    if args.web and not args.reset_data:
        _emit_runtime_trust_info(runtime_trust, to_stdout=True, to_stderr=True)
        import uvicorn
        from api.routes import app
        from core.host_resolution import resolve_api_host

        api_cfg = config.get("api", {})
        port = api_cfg.get("port", args.port)
        workers = int(api_cfg.get("workers", 1))
        host = resolve_api_host(config, cli_host=args.host)
        from core.host_resolution import should_warn_insecure_api_bind

        if should_warn_insecure_api_bind(config, host):
            print(
                "WARNING: API bind is non-loopback (%s) but api.require_api_key is not "
                "effectively enabled. Set api.require_api_key: true and a strong "
                "api.api_key (or api_key_from_env), or keep host 127.0.0.1 / reverse proxy. "
                "See SECURITY.md and docs/USAGE.md." % (host,),
                file=sys.stderr,
            )
        uvicorn.run(app, host=host, port=port, workers=workers)
        return

    engine = AuditEngine(config)

    if args.reset_data:
        _emit_runtime_trust_info(runtime_trust, to_stdout=True, to_stderr=True)
        # Require explicit confirmation: no undo, no going back.
        print()
        print("*** WIPE ALL GATHERED DATA ***")
        print()
        print("This will permanently:")
        print(
            "  - Remove all scan sessions, findings and failures from the SQLite database"
        )
        print(
            "  - Delete all generated Excel reports and heatmap PNGs under report.output_dir"
        )
        print()
        print("There is NO going back after this step. There is NO undo button.")
        print("Only a log entry in the database will record that a wipe was performed.")
        print()
        try:
            answer = (
                input("Type 'yes' to confirm and proceed, or anything else to abort: ")
                .strip()
                .lower()
            )
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
        print(
            "Existing Excel reports and heatmap PNGs under report.output_dir were deleted where possible."
        )
        print(
            "An audit entry was recorded in the data_wipe_log table for transparency."
        )
        return

    # Optional: warn when configured rate limits would block API scans for this config.
    rate_cfg = config.get("rate_limit") or {}
    if rate_cfg.get("enabled"):
        db_path = config.get("sqlite_path", "audit_results.db")
        dbm = LocalDBManager(db_path)
        running = dbm.get_running_sessions_count()
        last = dbm.get_last_session()
        max_concurrent = int(rate_cfg.get("max_concurrent_scans", 1))
        min_interval = int(rate_cfg.get("min_interval_seconds", 0))
        warn_lines: list[str] = []
        if running >= max_concurrent:
            warn_lines.append(
                f"rate_limit: there are already {running} running scan(s); "
                f"max_concurrent_scans={max_concurrent}. API calls would be rate-limited in this state."
            )
        if min_interval > 0 and last and last.get("started_at"):
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            started_at = last["started_at"]
            if started_at <= now:
                delta = (now - started_at).total_seconds()
                if delta < float(min_interval):
                    warn_lines.append(
                        f"rate_limit: last scan started {int(delta)}s ago; "
                        f"min_interval_seconds={min_interval}. Back-to-back API scans would be rejected "
                        "until the interval elapses."
                    )
        if warn_lines:
            print("[rate_limit] WARNING:")
            for ln in warn_lines:
                print("  - " + ln)
            print(
                "CLI will continue, but consider adjusting rate_limit settings if this is unexpected."
            )

    from core.validation import sanitize_tenant_technician

    tenant = sanitize_tenant_technician(args.tenant)
    technician = sanitize_tenant_technician(args.technician)
    # scan_compressed / use_content_type already merged above when CLI flags were passed
    try:
        _emit_runtime_trust_info(runtime_trust, to_stdout=True, to_stderr=True)
        session_id = engine.start_audit(tenant_name=tenant, technician_name=technician)
        print(f"Scan session: {session_id}")
        report_path = engine.generate_final_reports(session_id)
        if report_path:
            print(f"Report written: {report_path}")
        else:
            print("No findings to report.")
        from utils.notify import notify_scan_complete_background

        notify_scan_complete_background(engine.config, engine.db_manager, session_id)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(
            "Probable cause: A target path or file (e.g. DB, report output dir) is missing."
        )
        print(
            "What to do: Ensure paths in config exist; create report.output_dir if needed."
        )
        sys.exit(1)
    except (ConnectionError, OSError) as e:
        print(f"Error: {e}")
        print("Probable cause: Cannot access a resource (DB, disk, network target).")
        print(
            "What to do: Check permissions, disk space, and that no other process locks the DB or files."
        )
        sys.exit(1)
    except ModuleNotFoundError as e:
        print(f"Error: {e}")
        print(
            "Probable cause: An optional dependency (e.g. for 7z or a connector) is not installed."
        )
        print(
            "What to do: Install the optional extra, e.g. uv sync --extra compressed for 7z support."
        )
        sys.exit(1)
    except (ValueError, KeyError) as e:
        print(f"Error: {e}")
        print("Probable cause: Configuration or target definition is invalid.")
        print(
            "What to do: Check config against docs/USAGE.md and ensure all required keys are set."
        )
        sys.exit(1)
    except LicenseBlockedError as e:
        print(f"Licensing: scan blocked ({e.state}).", file=sys.stderr)
        print(str(e), file=sys.stderr)
        print(
            "What to do: Provide a valid license file and verify key (see docs/LICENSING_SPEC.md).",
            file=sys.stderr,
        )
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}")
        print("Probable cause: Unexpected failure during scan or report generation.")
        print(
            "What to do: Check logs and config; run with a minimal config to isolate the failing target."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
