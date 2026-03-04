"""
Single report generator: reads database_findings, filesystem_findings, scan_failures from LocalDBManager
for a session; produces Excel with sheets "Report info" (session + about), "Database findings", etc.,
and heatmap image (sensitivity/risk) with about footer. Returns path to Excel file.
"""
from pathlib import Path
from typing import Any

import pandas as pd

from core.about import get_about_info
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


_SENSITY_RANK = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}


def _excel_safe_sheet_title(title: str) -> str:
    """Return an Excel-safe worksheet title (max 31 chars, no []:*?/\\)."""
    invalid = set("[]:*?/\\")
    cleaned = "".join("-" if c in invalid else c for c in (title or "Sheet"))
    cleaned = cleaned.strip() or "Sheet"
    return cleaned[:31]


def _filter_by_min_sensitivity(rows: list[dict], min_sensitivity: str) -> list[dict]:
    """Keep only rows with sensitivity_level >= min_sensitivity (HIGH > MEDIUM > LOW)."""
    if not min_sensitivity or (min_sensitivity or "").upper() == "LOW":
        return rows
    min_rank = _SENSITY_RANK.get((min_sensitivity or "").upper(), 1)
    return [r for r in rows if _SENSITY_RANK.get((r.get("sensitivity_level") or "").upper(), 1) >= min_rank]


def _create_heatmap(db_rows: list[dict], fs_rows: list[dict], output_dir: str, session_id: str) -> str | None:
    """Build sensitivity/risk heatmap from DB + filesystem findings; save PNG with about footer. Return path or None."""
    if not _PLOT_AVAILABLE:
        return None
    rows = []
    for r in db_rows:
        rows.append({"target": r.get("target_name", ""), "source": "database", "sensitivity": r.get("sensitivity_level", "LOW")})
    for r in fs_rows:
        rows.append({"target": r.get("target_name", ""), "source": "filesystem", "sensitivity": r.get("sensitivity_level", "LOW")})
    if not rows:
        return None
    about = get_about_info()
    df = pd.DataFrame(rows)
    pivot = df.groupby(["target", "sensitivity"]).size().unstack(fill_value=0)
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, cmap="YlOrRd", fmt="d", cbar_kws={"label": "Findings"})
    plt.title("Sensitivity / Risk Heatmap")
    # About footer on the image (detached heatmap carries app credit and license)
    footer = f"{about['name']} v{about['version']} · {about['author']} · {about['license']}"
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.12)
    plt.figtext(0.5, 0.02, footer, ha="center", fontsize=7, style="italic")
    out_path = Path(output_dir) / f"heatmap_{session_id[:12]}.png"
    plt.savefig(out_path, bbox_inches="tight")
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


def _recommendations_rows(
    db_rows: list[dict],
    fs_rows: list[dict],
    recommendation_overrides: list[dict] | None = None,
) -> list[dict]:
    """
    Build recommendations from unique pattern_detected and norm_tag.
    Each row explains what kind of personal/sensitive data was inferred, which legal norm might apply,
    why it matters (risk description), and what action DPO / Security / Compliance teams should consider.
    If recommendation_overrides is provided, entries are matched by norm_tag (substring or exact);
    keys: norm_tag_pattern, base_legal, risk, recommendation, priority, relevant_for.
    """
    overrides = recommendation_overrides or []
    seen = set()
    recs = []
    for r in db_rows + fs_rows:
        pat = r.get("pattern_detected") or ""
        norm = r.get("norm_tag") or ""
        key = (pat, norm)
        if key in seen or not pat:
            continue
        seen.add(key)
        # Match override: norm_tag_pattern matches if it is a substring of norm or norm is a substring of it
        override_row = None
        for o in overrides:
            pattern_str = (o.get("norm_tag_pattern") or "").strip()
            if not pattern_str:
                continue
            if pattern_str in norm or norm in pattern_str:
                override_row = {
                    "Data / Pattern": pat,
                    "Base legal": o.get("base_legal", norm or "-"),
                    "Risco": o.get("risk", "-"),
                    "Recomendação": o.get("recommendation", "-"),
                    "Prioridade": o.get("priority", "MÉDIA"),
                    "Relevante para": o.get("relevant_for", "DPO, Segurança da Informação"),
                }
                break
        if override_row:
            recs.append(override_row)
            continue
        # Possible data of minors (LGPD Art. 14, GDPR Art. 8) – highest priority, differential treatment
        if "DOB_POSSIBLE_MINOR" in pat or ("LGPD Art. 14" in norm and ("menor" in norm.lower() or "minor" in norm.lower())):
            recs.append({
                "Data / Pattern": pat,
                "Base legal": norm or "LGPD Art. 14 (dados de crianças/adolescentes); GDPR Art. 8 (consentimento em serviços da sociedade da informação)",
                "Risco": "Dados que podem se referir a menores de idade: tratamento sujeito a bases legais específicas, consentimento do titular ou dos pais/responsáveis e restrições de armazenamento, uso e compartilhamento.",
                "Recomendação": (
                    "Caso especial – dados de menores: (1) Garantir base legal e consentimento válido (titular ou responsável, conforme a idade e a lei aplicável). "
                    "(2) Restringir armazenamento ao estritamente necessário; evitar retenção além do prazo. "
                    "(3) Limitar uso e compartilhamento ao que for autorizado; não compartilhar com terceiros sem base legal e consentimento. "
                    "(4) Revisar políticas de privacidade e termos para tratamento de dados de crianças/adolescentes (LGPD Art. 14; GDPR Art. 8). "
                    "(5) Priorizar anonimização ou pseudonimização quando possível; controle de acesso rigoroso."
                ),
                "Prioridade": "CRÍTICA",
                "Relevante para": "DPO, Compliance, Área jurídica, Segurança da Informação",
            })
            continue
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
    # Surface possible-minor recommendations first (highest priority for DPO/compliance)
    def _is_minor_rec(row: dict) -> bool:
        pat = (row.get("Data / Pattern") or "").strip()
        base = (row.get("Base legal") or "").lower()
        return "DOB_POSSIBLE_MINOR" in pat or ("art. 14" in base and ("menor" in base or "minor" in base or "child" in base))
    recs.sort(key=lambda r: (0 if _is_minor_rec(r) else 1, r.get("Data / Pattern", "")))
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


def generate_report(
    db_manager: Any,
    session_id: str,
    output_dir: str = ".",
    config: dict | None = None,
) -> str | None:
    """
    Read session from db_manager (database_findings, filesystem_findings, scan_failures);
    write Excel and heatmap. Return path to Excel file or None.
    Includes "Report info" (session + tenant), "Trends - Session comparison" when previous run exists.
    Optional config: if provided, report.recommendation_overrides and other report options are applied.
    """
    db_rows, fs_rows, fail_rows = db_manager.get_findings(session_id)
    if not db_rows and not fs_rows and not fail_rows:
        return None
    current_db = len(db_rows)
    current_fs = len(fs_rows)
    current_fail = len(fail_rows)
    # Optional filter: only include findings with sensitivity >= report.min_sensitivity (for findings sheets, recommendations, heatmap)
    report_cfg = (config or {}).get("report", {}) if isinstance((config or {}).get("report"), dict) else {}
    min_sens = (report_cfg.get("min_sensitivity") or "LOW").upper()
    if min_sens != "LOW":
        db_rows_for_sheets = _filter_by_min_sensitivity(db_rows, min_sens)
        fs_rows_for_sheets = _filter_by_min_sensitivity(fs_rows, min_sens)
    else:
        db_rows_for_sheets = db_rows
        fs_rows_for_sheets = fs_rows
    # Session metadata for trends and report info sheet
    current_started_at = None
    tenant_name = None
    technician_name = None
    config_scope_hash = None
    for s in (db_manager.list_sessions() or []):
        if s.get("session_id") == session_id:
            current_started_at = s.get("started_at")
            tenant_name = s.get("tenant_name")
            technician_name = s.get("technician_name")
            config_scope_hash = s.get("config_scope_hash")
            break
    about = get_about_info()
    out_path = Path(output_dir) / f"Relatorio_Auditoria_{session_id[:16]}.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        # Report info sheet: session + tenant/technician + about (application, author, license)
        report_info = [
            {"Field": "Session ID", "Value": session_id},
            {"Field": "Started at", "Value": current_started_at or "—"},
            {"Field": "Tenant / Customer", "Value": tenant_name or "—"},
            {"Field": "Technician / Operator", "Value": technician_name or "—"},
        ]
        if config_scope_hash:
            report_info.append({"Field": "Config scope hash", "Value": config_scope_hash})
        report_info.extend([
            {"Field": "Application", "Value": about["name"]},
            {"Field": "Version", "Value": about["version"]},
            {"Field": "Author", "Value": about["author"]},
            {"Field": "License", "Value": about["license"]},
            {"Field": "Copyright", "Value": about["copyright"]},
        ])
        pd.DataFrame(report_info).to_excel(writer, sheet_name="Report info", index=False)
        # Optional Executive summary: counts by sensitivity, by norm_tag, top targets
        include_exec = report_cfg.get("include_executive_summary", False)
        if include_exec and (db_rows_for_sheets or fs_rows_for_sheets):
            exec_rows: list[dict] = []
            all_findings = db_rows_for_sheets + fs_rows_for_sheets
            for level in ("HIGH", "MEDIUM", "LOW"):
                count = sum(1 for r in all_findings if (r.get("sensitivity_level") or "").upper() == level)
                exec_rows.append({"Metric": f"Findings by sensitivity", "Category": level, "Count": count})
            norm_counts: dict[str, int] = {}
            for r in all_findings:
                nt = (r.get("norm_tag") or "").strip() or "(no norm_tag)"
                norm_counts[nt] = norm_counts.get(nt, 0) + 1
            for nt, count in sorted(norm_counts.items(), key=lambda x: -x[1]):
                exec_rows.append({"Metric": "Findings by Framework / Norm", "Category": nt, "Count": count})
            target_counts: dict[str, int] = {}
            for r in all_findings:
                t = (r.get("target_name") or "").strip() or "(unknown)"
                target_counts[t] = target_counts.get(t, 0) + 1
            top_n = 10
            for t, count in sorted(target_counts.items(), key=lambda x: -x[1])[:top_n]:
                exec_rows.append({"Metric": "Top targets by finding count", "Category": t, "Count": count})
            pd.DataFrame(exec_rows).to_excel(writer, sheet_name="Executive summary", index=False)
        if db_rows_for_sheets:
            pd.DataFrame(db_rows_for_sheets).to_excel(writer, sheet_name="Database findings", index=False)
        if fs_rows_for_sheets:
            pd.DataFrame(fs_rows_for_sheets).to_excel(writer, sheet_name="Filesystem findings", index=False)
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
        overrides = report_cfg.get("recommendation_overrides", [])
        recs = _recommendations_rows(db_rows_for_sheets, fs_rows_for_sheets, recommendation_overrides=overrides if overrides else None)
        pd.DataFrame(recs).to_excel(writer, sheet_name="Recommendations", index=False)
        praise = _praise_rows(db_rows_for_sheets, fs_rows_for_sheets)
        if praise:
            pd.DataFrame(praise).to_excel(
                writer,
                sheet_name=_excel_safe_sheet_title("Praise / existing controls"),
                index=False,
            )
        # Trends: compare with previous run for DPO and security team
        trends = _trends_rows(
            db_manager, session_id,
            current_db, current_fs, current_fail, current_started_at,
        )
        pd.DataFrame(trends).to_excel(writer, sheet_name="Trends - Session comparison", index=False)
        # Summary heatmap data as sheet
        rows = [{"target": r.get("target_name"), "sensitivity": r.get("sensitivity_level")} for r in db_rows_for_sheets + fs_rows_for_sheets]
        if rows:
            summary = pd.DataFrame(rows).groupby(["target", "sensitivity"]).size().unstack(fill_value=0)
            summary.to_excel(writer, sheet_name="Heatmap data")
    _create_heatmap(db_rows_for_sheets, fs_rows_for_sheets, output_dir, session_id)
    return str(out_path)
