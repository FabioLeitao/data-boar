"""
Single report generator: reads database_findings, filesystem_findings, scan_failures from LocalDBManager
for a session; produces Excel with sheets "Database findings", "Filesystem findings", "Scan failures",
"Recommendations", "Praise / existing controls", "Trends - Session comparison", and heatmap image (sensitivity/risk).
Returns path to Excel file.
"""
from pathlib import Path
from typing import Any

import pandas as pd

from core.database import failure_hint

# Optional matplotlib/seaborn for heatmap
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    _PLOT_AVAILABLE = True
except ImportError:
    _PLOT_AVAILABLE = False


def _create_heatmap(db_rows: list[dict], fs_rows: list[dict], output_dir: str, session_id: str) -> str | None:
    """Build sensitivity/risk heatmap from DB + filesystem findings; save PNG. Return path or None."""
    if not _PLOT_AVAILABLE:
        return None
    rows = []
    for r in db_rows:
        rows.append({"target": r.get("target_name", ""), "source": "database", "sensitivity": r.get("sensitivity_level", "LOW")})
    for r in fs_rows:
        rows.append({"target": r.get("target_name", ""), "source": "filesystem", "sensitivity": r.get("sensitivity_level", "LOW")})
    if not rows:
        return None
    df = pd.DataFrame(rows)
    pivot = df.groupby(["target", "sensitivity"]).size().unstack(fill_value=0)
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, cmap="YlOrRd", fmt="d", cbar_kws={"label": "Findings"})
    plt.title("Sensitivity / Risk Heatmap")
    plt.tight_layout()
    out_path = Path(output_dir) / f"heatmap_{session_id[:12]}.png"
    plt.savefig(out_path)
    plt.close()
    return str(out_path)


# Keywords that suggest existing data protection (column name or pattern_detected)
_PRAISE_KEYWORDS = ("encrypted", "hash", "hashed", "tokenized", "token", "masked", "mask", "pseudonym", "anon", "redact", "hmac", "cipher")


def _praise_rows(db_rows: list[dict], fs_rows: list[dict]) -> list[dict]:
    """
    Build rows for "Praise / existing controls": findings where column name or pattern_detected
    suggests existing protections (encryption, hashing, tokenization, masking, etc.).
    """
    rows = []
    for r, source in [(x, "database") for x in db_rows] + [(x, "filesystem") for x in fs_rows]:
        col = (r.get("column_name") or r.get("file_name") or "").lower()
        pat = (r.get("pattern_detected") or "").lower()
        combined = f"{col} {pat}"
        for kw in _PRAISE_KEYWORDS:
            if kw in combined:
                rows.append({
                    "Target": r.get("target_name", ""),
                    "Source": source,
                    "Column / File": r.get("column_name") or r.get("file_name") or "-",
                    "Pattern detected": r.get("pattern_detected", ""),
                    "Indication": f"Possible protection: '{kw}'",
                })
                break
    return rows


def _recommendations_rows(db_rows: list[dict], fs_rows: list[dict]) -> list[dict]:
    """
    Build recommendations from unique pattern_detected and norm_tag.
    Each row explains what kind of personal/sensitive data was inferred, which legal norm might apply,
    why it matters (risk description), and what action DPO / Security / Compliance teams should consider.
    """
    seen = set()
    recs = []
    for r in db_rows + fs_rows:
        pat = r.get("pattern_detected") or ""
        norm = r.get("norm_tag") or ""
        key = (pat, norm)
        if key in seen or not pat:
            continue
        seen.add(key)
        if "CPF" in pat or "SSN" in pat or "LGPD" in norm:
            recs.append({
                "Data / Pattern": pat,
                "Base legal": norm or "LGPD/GDPR – identificação direta",
                "Risco": "Identificação direta de pessoa natural (dados de cadastro/identidade).",
                "Recomendação": "Anonimização ou hashing; restringir acesso (Least Privilege); revisar base legal e minimização.",
                "Prioridade": "CRÍTICA",
                "Relevante para": "DPO, Segurança da Informação, Compliance",
            })
        elif "EMAIL" in pat:
            recs.append({
                "Data / Pattern": pat,
                "Base legal": norm or "LGPD/GDPR – contato eletrônico",
                "Risco": "Vazamento de endereços de e-mail e possível uso indevido em campanhas/comunicações.",
                "Recomendação": "Criptografia da coluna; revisão de logs de acesso; validação de consentimento e opt-out.",
                "Prioridade": "ALTA",
                "Relevante para": "DPO, Marketing, Segurança da Informação",
            })
        elif "CREDIT" in pat or "CARD" in pat:
            recs.append({
                "Data / Pattern": pat,
                "Base legal": norm or "LGPD/GDPR – dados financeiros / PCI-DSS",
                "Risco": "Fraude financeira, chargeback e exposição de dados de cartão/conta.",
                "Recomendação": "Não armazenar número completo; tokenização; mascaramento; conformidade PCI-DSS e políticas internas.",
                "Prioridade": "CRÍTICA",
                "Relevante para": "DPO, Segurança da Informação, Risco/Compliance financeiro",
            })
        else:
            recs.append({
                "Data / Pattern": pat,
                "Base legal": norm or "LGPD/GDPR/CCPA – dado pessoal ou sensível",
                "Risco": "Dado pessoal ou sensível com possível aumento de superfície de exposição.",
                "Recomendação": "Avaliar necessidade do tratamento; aplicar pseudonimização ou criptografia; reforçar controle de acesso.",
                "Prioridade": "MÉDIA",
                "Relevante para": "DPO, Segurança da Informação",
            })
    if not recs:
        recs.append({
            "Data / Pattern": "-",
            "Base legal": "-",
            "Risco": "Nenhum achado crítico nesta sessão",
            "Recomendação": "Manter boas práticas de proteção de dados.",
            "Prioridade": "INFO",
            "Relevante para": "DPO, Segurança da Informação",
        })
    return recs


def _trends_rows(
    db_manager: Any,
    session_id: str,
    current_db: int,
    current_fs: int,
    current_fail: int,
    current_started_at: str | None,
) -> list[dict]:
    """
    Build rows for "Trends - Session comparison": compare this run with the previous run
    to show improvements (fewer findings) or new or increased findings for DPO and security team.
    """
    prev = db_manager.get_previous_session(session_id) if hasattr(db_manager, "get_previous_session") else None
    rows = []

    def _change_note(curr: int, prev_val: int | None, metric_label: str) -> str:
        if prev_val is None:
            return "First run or no previous session to compare."
        delta = curr - prev_val
        if delta < 0:
            return f"Improvement: {metric_label} reduced by {abs(delta)} (fewer violations or sensitive data exposure)."
        if delta > 0:
            return f"New or increased: {metric_label} increased by {delta} – review sheet for details; may require DPO action."
        return "No change from previous run."

    # Total findings (DB + FS) – main compliance indicator
    total_current = current_db + current_fs
    total_prev = (prev["database_findings"] + prev["filesystem_findings"]) if prev else None
    rows.append({
        "Metric": "Total findings (DB + filesystem)",
        "This run (count)": total_current,
        "This run (date)": current_started_at or "-",
        "Previous run (count)": total_prev if total_prev is not None else "-",
        "Previous run (date)": prev.get("started_at") if prev else "-",
        "Change": (total_current - total_prev) if total_prev is not None else "-",
        "Note": _change_note(total_current, total_prev, "Total findings"),
    })
    rows.append({
        "Metric": "Database findings",
        "This run (count)": current_db,
        "This run (date)": current_started_at or "-",
        "Previous run (count)": prev.get("database_findings") if prev else "-",
        "Previous run (date)": prev.get("started_at") if prev else "-",
        "Change": (current_db - prev["database_findings"]) if prev else "-",
        "Note": _change_note(current_db, prev["database_findings"] if prev else None, "Database findings"),
    })
    rows.append({
        "Metric": "Filesystem findings",
        "This run (count)": current_fs,
        "This run (date)": current_started_at or "-",
        "Previous run (count)": prev.get("filesystem_findings") if prev else "-",
        "Previous run (date)": prev.get("started_at") if prev else "-",
        "Change": (current_fs - prev["filesystem_findings"]) if prev else "-",
        "Note": _change_note(current_fs, prev["filesystem_findings"] if prev else None, "Filesystem findings"),
    })
    rows.append({
        "Metric": "Scan failures (targets not scanned)",
        "This run (count)": current_fail,
        "This run (date)": current_started_at or "-",
        "Previous run (count)": prev.get("scan_failures") if prev else "-",
        "Previous run (date)": prev.get("started_at") if prev else "-",
        "Change": (current_fail - prev["scan_failures"]) if prev else "-",
        "Note": _change_note(current_fail, prev["scan_failures"] if prev else None, "Scan failures"),
    })
    return rows


def generate_report(db_manager: Any, session_id: str, output_dir: str = ".") -> str | None:
    """
    Read session from db_manager (database_findings, filesystem_findings, scan_failures);
    write Excel and heatmap. Return path to Excel file or None.
    Includes "Report info" (session + tenant), "Trends - Session comparison" when previous run exists.
    """
    db_rows, fs_rows, fail_rows = db_manager.get_findings(session_id)
    if not db_rows and not fs_rows and not fail_rows:
        return None
    current_db = len(db_rows)
    current_fs = len(fs_rows)
    current_fail = len(fail_rows)
    # Session metadata for trends and report info sheet
    current_started_at = None
    tenant_name = None
    technician_name = None
    for s in (db_manager.list_sessions() or []):
        if s.get("session_id") == session_id:
            current_started_at = s.get("started_at")
            tenant_name = s.get("tenant_name")
            technician_name = s.get("technician_name")
            break
    out_path = Path(output_dir) / f"Relatorio_Auditoria_{session_id[:16]}.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        # Report info sheet: session id, started at, tenant/customer, technician/operator (first so it's visible when opening)
        report_info = [
            {"Field": "Session ID", "Value": session_id},
            {"Field": "Started at", "Value": current_started_at or "—"},
            {"Field": "Tenant / Customer", "Value": tenant_name or "—"},
            {"Field": "Technician / Operator", "Value": technician_name or "—"},
        ]
        pd.DataFrame(report_info).to_excel(writer, sheet_name="Report info", index=False)
        if db_rows:
            pd.DataFrame(db_rows).to_excel(writer, sheet_name="Database findings", index=False)
        if fs_rows:
            pd.DataFrame(fs_rows).to_excel(writer, sheet_name="Filesystem findings", index=False)
        if fail_rows:
            enriched_failures: list[dict] = []
            for r in fail_rows:
                reason = r.get("reason") or "error"
                enriched_failures.append(
                    {
                        **r,
                        "Category": reason,
                        "Impact": "Target was not fully scanned; overall coverage for this environment is incomplete until this issue is fixed.",
                        "Suggested next step": failure_hint(reason),
                    }
                )
            pd.DataFrame(enriched_failures).to_excel(writer, sheet_name="Scan failures", index=False)
        recs = _recommendations_rows(db_rows, fs_rows)
        pd.DataFrame(recs).to_excel(writer, sheet_name="Recommendations", index=False)
        praise = _praise_rows(db_rows, fs_rows)
        if praise:
            pd.DataFrame(praise).to_excel(writer, sheet_name="Praise / existing controls", index=False)
        # Trends: compare with previous run for DPO and security team
        trends = _trends_rows(
            db_manager, session_id,
            current_db, current_fs, current_fail, current_started_at,
        )
        pd.DataFrame(trends).to_excel(writer, sheet_name="Trends - Session comparison", index=False)
        # Summary heatmap data as sheet
        rows = [{"target": r.get("target_name"), "sensitivity": r.get("sensitivity_level")} for r in db_rows + fs_rows]
        if rows:
            summary = pd.DataFrame(rows).groupby(["target", "sensitivity"]).size().unstack(fill_value=0)
            summary.to_excel(writer, sheet_name="Heatmap data")
    _create_heatmap(db_rows, fs_rows, output_dir, session_id)
    return str(out_path)
