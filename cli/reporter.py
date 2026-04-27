"""
CLI ``data-boar-report``: executive Markdown from local SQLite (same core as ``POC_SUMMARY_*.md``).

Enterprise data discovery & risk governance desk output — no live connector required.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from config.loader import load_config
from core.about import get_about_info
from core.database import LocalDBManager
from report.executive_report import generate_executive_report
from report.safe_prefix import safe_session_prefix
from report.scan_evidence import _aggregate_apg, _build_manifest


def _session_meta(db_manager: LocalDBManager, session_id: str) -> dict[str, Any]:
    for s in db_manager.list_sessions() or []:
        if s.get("session_id") == session_id:
            return {
                "started_at": s.get("started_at"),
                "finished_at": s.get("finished_at"),
                "tenant_name": s.get("tenant_name"),
                "technician_name": s.get("technician_name"),
                "config_scope_hash": s.get("config_scope_hash"),
                "jurisdiction_hint": bool(s.get("jurisdiction_hint")),
            }
    return {
        "started_at": None,
        "finished_at": None,
        "tenant_name": None,
        "technician_name": None,
        "config_scope_hash": None,
        "jurisdiction_hint": False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=(
            "Data Boar — enterprise data discovery & risk governance: regenerate executive Markdown "
            "(methodology, security evidence, full APG inventory, Top 3 priorities) from local SQLite "
            "for a completed scan session."
        )
    )
    p.add_argument(
        "--config",
        required=True,
        help="Caminho do YAML de configuração (usa sqlite_path salvo no scan).",
    )
    p.add_argument(
        "--session-id",
        required=True,
        dest="session_id",
        help="ID da sessão (UUID) gravado em scan_sessions.",
    )
    p.add_argument(
        "-o",
        "--output",
        default="",
        help=(
            "Arquivo .md de saída. Se omitido, grava ao lado do YAML de config: "
            "`executive_report_<prefix>.md` (evita expor relatório em stdout/logs de CI)."
        ),
    )
    p.add_argument(
        "--sqlite",
        default="",
        help="Sobrescreve sqlite_path do config (útil em homelab sem editar YAML).",
    )
    p.add_argument(
        "--trial-rows-capped",
        action="store_true",
        help="Propaga nota de linhas limitadas no Excel (licença trial).",
    )
    args = p.parse_args(argv)

    cfg_path = Path(args.config).expanduser().resolve()
    cfg = load_config(cfg_path)
    db_path = (args.sqlite or "").strip() or str(
        cfg.get("sqlite_path") or "audit_results.db"
    )
    sid = (args.session_id or "").strip()
    if not sid:
        print("session-id vazio", file=sys.stderr)
        return 2

    mgr = LocalDBManager(db_path)
    try:
        db_rows, fs_rows, fail_rows = mgr.get_findings(sid)
        meta = _session_meta(mgr, sid)
        about = get_about_info()
        manifest = _build_manifest(
            session_id=sid,
            meta=meta,
            about=about,
            config=cfg if isinstance(cfg, dict) else {},
            db_rows=db_rows,
            fs_rows=fs_rows,
            fail_rows=fail_rows,
            report_rows_capped=bool(args.trial_rows_capped),
        )
        apg_rows = _aggregate_apg(db_rows, fs_rows)
        md = generate_executive_report(
            session_id=sid,
            about=about,
            manifest=manifest,
            db_rows=db_rows,
            fs_rows=fs_rows,
            _fail_rows=fail_rows,
            apg_rows=apg_rows,
            report_rows_capped=bool(args.trial_rows_capped),
        )
        out_arg = (args.output or "").strip()
        if out_arg:
            out = Path(out_arg).expanduser().resolve()
        else:
            prefix = safe_session_prefix(sid, max_len=8)
            base = cfg_path.parent.resolve()
            out = (base / f"executive_report_{prefix}.md").resolve()
            if not out.is_relative_to(base):
                print("refuse output path outside config directory", file=sys.stderr)
                return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        return 0
    finally:
        mgr.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
