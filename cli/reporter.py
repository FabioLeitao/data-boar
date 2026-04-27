"""
CLI ``data-boar-report``: executive Markdown from local SQLite (same core as ``POC_SUMMARY_*.md``).

Enterprise data discovery & risk governance desk output -- no live connector required.

Doctrine references (when this CLI fails or has to fall back, the operator and the
agent both deserve a Sysinternals-grade narrative, not a one-line stack trace):

- ``docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`` -- never silently fall through.
- ``docs/ops/inspirations/INTERNAL_DIAGNOSTIC_AESTHETICS.md`` -- the failure block
  must name the phase, the exit code, narrow the hypothesis space, and point at
  the next concrete check.
- ``docs/ops/inspirations/ACTIONABLE_GOVERNANCE_AND_TRUST.md`` -- the executive
  Markdown is part of the "trust triangle" (Markdown + manifest YAML + reproducible
  CLI). A failure here must protect that triangle, never paper it over.
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


def _emit_rca_block(
    *,
    phase: str,
    symptom: str,
    hypotheses: list[str],
    next_step: str,
    exit_code: int,
) -> None:
    """Print a Sysinternals-style RCA block for ``data-boar-report`` failures.

    The block is intentionally short and human-readable; it is meant for the
    Cursor/PowerShell terminal an operator (or this SRE agent) sees right after
    a failed invocation. It also gives the lab orchestrator a stable string to
    quote in completao logs.

    The CLI's exit code is the canonical signal; the block adds context, it
    does not replace ``return`` / non-zero exits.
    """
    print(f"--- RCA (data-boar-report phase={phase}) ---", file=sys.stderr)
    print(f"symptom : {symptom}", file=sys.stderr)
    print(f"exit    : {exit_code}", file=sys.stderr)
    if hypotheses:
        print("hypotheses (narrow):", file=sys.stderr)
        for h in hypotheses:
            print(f"  - {h}", file=sys.stderr)
    if next_step:
        print(f"next    : {next_step}", file=sys.stderr)
    print(
        "doctrine: docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md, "
        "INTERNAL_DIAGNOSTIC_AESTHETICS.md",
        file=sys.stderr,
    )
    print("--- end RCA ---", file=sys.stderr)


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
        _emit_rca_block(
            phase="parse_args",
            symptom="--session-id is empty after trimming.",
            hypotheses=[
                "The caller forgot to pass --session-id (CLI contract violation).",
                "A wrapper script substituted an empty variable.",
            ],
            next_step=(
                "Re-run with --session-id <UUID>; list available ids with: "
                'uv run python -c "from core.database import LocalDBManager as M; '
                "import sys; m=M(sys.argv[1]);"
                " print([s.get('session_id') for s in m.list_sessions() or []])\" <sqlite_path>"
            ),
            exit_code=2,
        )
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
                _emit_rca_block(
                    phase="output_path_guard",
                    symptom=(
                        "Resolved default output path escapes the config "
                        "directory; refusing to write."
                    ),
                    hypotheses=[
                        "Symlink or junction in the config directory aimed outside it.",
                        "safe_session_prefix returned a value containing path separators.",
                    ],
                    next_step=(
                        "Pass an explicit -o <file.md> under a directory you control; "
                        "or run from a clean config directory without symlinks."
                    ),
                    exit_code=2,
                )
                return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        return 0
    except Exception as exc:
        # Fallback doctrine: the trust triangle (Markdown + manifest YAML +
        # reproducible CLI) must remain auditable. We surface a structured RCA
        # block so completao logs and the operator both get the same prose,
        # then re-raise so existing pytest / CI behaviour is unchanged.
        _emit_rca_block(
            phase="generate_executive_markdown",
            symptom=f"{type(exc).__name__}: {exc}",
            hypotheses=[
                "SQLite path is wrong (cfg.sqlite_path or --sqlite override).",
                "session-id does not match any row in scan_sessions.",
                "scan_evidence._build_manifest raised on a malformed config dict.",
                "Output directory is read-only or full.",
            ],
            next_step=(
                "Verify cfg.sqlite_path with sqlite3 <path> '.tables'; "
                "list session ids before retry; "
                "for full traceback re-run with PYTHONFAULTHANDLER=1."
            ),
            exit_code=1,
        )
        raise
    finally:
        mgr.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
