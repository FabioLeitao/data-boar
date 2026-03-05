"""
Single report generator: reads database_findings, filesystem_findings, scan_failures from LocalDBManager
for a session; produces Excel with sheets "Report info" (session + about), "Database findings", etc.,
and heatmap image (sensitivity/risk) with about footer. Returns path to Excel file.

Structure: generate_report() delegates all sheet writing to _write_excel_sheets() and helpers
(_build_report_info, _build_executive_summary_rows, etc.). Keep sheet logic in those helpers
so branches stay in sync with main and merge conflicts are avoided (see CONTRIBUTING.md).
"""
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from core.about import get_about_info
from core.aggregated_identification import run_aggregation
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

# Patterns/names that suggest identifier or health (for minor cross-reference: same table has DOB/minor + name/doc/health)
_IDENTIFIER_OR_HEALTH_PATTERNS = ("LGPD_CPF", "CCPA_SSN", "EMAIL", "CPF", "SSN", "RG")
_IDENTIFIER_OR_HEALTH_COLUMN_TOKENS = (
    "nome", "name", "cpf", "rg", "ssn", "health", "saude", "cid", "prontuario", "diagnostic",
    "identidade", "identity", "documento", "document", "nascimento", "birth",
)

# Recommendation sheet column names (Excel output; avoid string literal duplication for Sonar S1192)
_REC_DATA_PATTERN = "Data / Pattern"
_REC_BASE_LEGAL = "Base legal"
_REC_RISCO = "Risco"
_REC_RECOMENDACAO = "Recomendação"
_REC_PRIORIDADE = "Prioridade"
_REC_RELEVANTE_PARA = "Relevante para"
_REC_DEFAULT_RELEVANTE = "DPO, Segurança da Informação"
_REC_PRIORITY_CRITICA = "CRÍTICA"

# Trends sheet column names and metric labels (S1192)
_TREND_THIS_RUN_COUNT = "This run (count)"
_TREND_THIS_RUN_DATE = "This run (date)"
_TREND_PREV_RUN_COUNT = "Previous run (count)"
_TREND_PREV_RUN_DATE = "Previous run (date)"
_METRIC_TOTAL_FINDINGS = "Total findings (DB + filesystem)"
_METRIC_TOTAL_FINDINGS_LABEL = "Total findings"
_METRIC_DB_FINDINGS = "Database findings"
_METRIC_FS_FINDINGS = "Filesystem findings"
_METRIC_SCAN_FAILURES = "Scan failures (targets not scanned)"
_METRIC_SCAN_FAILURES_LABEL = "Scan failures"
_SHEET_DB_FINDINGS = "Database findings"
_SHEET_FS_FINDINGS = "Filesystem findings"
_SHEET_SCAN_FAILURES = "Scan failures"


def _change_note(curr: int, prev_val: int | None, metric_label: str) -> str:
    """Build a human-readable note for trends: first run, improvement, new/increased, or no change."""
    if prev_val is None:
        return "First run or no previous session to compare."
    delta = curr - prev_val
    if delta < 0:
        return f"Improvement: {metric_label} reduced by {abs(delta)} (fewer violations or sensitive data exposure)."
    if delta > 0:
        return f"New or increased: {metric_label} increased by {delta} – review sheet for details; may require DPO action."
    return "No change from previous run."


def _one_trend_row(
    metric_display: str,
    current_count: int,
    current_started_at: str | None,
    prev_val: int | None,
    prev_started_at: str | None,
    note_label: str,
) -> dict:
    """Build a single row for the Trends sheet (this run vs previous run)."""
    return {
        "Metric": metric_display,
        _TREND_THIS_RUN_COUNT: current_count,
        _TREND_THIS_RUN_DATE: current_started_at or "-",
        _TREND_PREV_RUN_COUNT: prev_val if prev_val is not None else "-",
        _TREND_PREV_RUN_DATE: prev_started_at or "-",
        "Change": (current_count - prev_val) if prev_val is not None else "-",
        "Note": _change_note(current_count, prev_val, note_label),
    }


def _row_suggests_identifier_or_health(row: dict) -> bool:
    """True if finding suggests name, official doc (CPF/RG/SSN), or health data (for cross-reference with possible minor)."""
    pat = (row.get("pattern_detected") or "").upper()
    col = (row.get("column_name") or row.get("file_name") or "").lower()
    for p in _IDENTIFIER_OR_HEALTH_PATTERNS:
        if p in pat:
            return True
    for t in _IDENTIFIER_OR_HEALTH_COLUMN_TOKENS:
        if t in col:
            return True
    return False


def _high_confidence_keys_for_groups(
    rows: list[dict],
    group_key: Callable[[dict], tuple],
    row_key: Callable[[dict], tuple],
) -> set[tuple]:
    """
    Group rows by group_key; for each group that has both DOB_POSSIBLE_MINOR and identifier/health
    findings, collect row_key(r) for every row in that group with DOB_POSSIBLE_MINOR. Return the set.
    """
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        grouped[group_key(r)].append(r)
    result: set[tuple] = set()
    for group_rows in grouped.values():
        has_minor = any("DOB_POSSIBLE_MINOR" in (r.get("pattern_detected") or "") for r in group_rows)
        has_id_or_health = any(_row_suggests_identifier_or_health(r) for r in group_rows)
        if not (has_minor and has_id_or_health):
            continue
        for r in group_rows:
            if "DOB_POSSIBLE_MINOR" in (r.get("pattern_detected") or ""):
                result.add(row_key(r))
    return result


def _minor_cross_reference_confidence(
    db_rows: list[dict],
    fs_rows: list[dict],
) -> tuple[set[tuple], set[tuple]]:
    """
    When DOB_POSSIBLE_MINOR appears in the same table (or same file) as identifier/health findings,
    return sets of keys for which to show 'high (cross-ref)' minor confidence.
    Returns (db_keys, fs_keys). DB key = (target_name, schema_name, table_name, column_name); FS key = (target_name, path, file_name).
    """
    db_high = _high_confidence_keys_for_groups(
        db_rows,
        lambda r: (r.get("target_name", ""), r.get("schema_name", ""), r.get("table_name", "")),
        lambda r: (r.get("target_name", ""), r.get("schema_name", ""), r.get("table_name", ""), r.get("column_name", "")),
    )
    fs_high = _high_confidence_keys_for_groups(
        fs_rows,
        lambda r: (r.get("target_name", ""), r.get("path", "")),
        lambda r: (r.get("target_name", ""), r.get("path", ""), r.get("file_name", "")),
    )
    return db_high, fs_high


def _apply_minor_confidence_column(
    rows: list[dict],
    high_confidence_keys: set[tuple],
    key_getter: Callable[[dict], tuple],
) -> None:
    """Mutate each row to add 'Minor confidence' = 'high (cross-ref)' for keys in high_confidence_keys, else ''."""
    for r in rows:
        k = key_getter(r)
        r["Minor confidence"] = "high (cross-ref)" if k in high_confidence_keys else ""


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


def _find_override_row(pat: str, norm: str, overrides: list[dict]) -> dict | None:
    """
    Find first override whose norm_tag_pattern matches norm (substring or exact).
    Return a recommendation row dict built from that override, or None.
    """
    for o in overrides:
        pattern_str = (o.get("norm_tag_pattern") or "").strip()
        if not pattern_str or (pattern_str not in norm and norm not in pattern_str):
            continue
        return {
            _REC_DATA_PATTERN: pat,
            _REC_BASE_LEGAL: o.get("base_legal", norm or "-"),
            _REC_RISCO: o.get("risk", "-"),
            _REC_RECOMENDACAO: o.get("recommendation", "-"),
            _REC_PRIORIDADE: o.get("priority", "MÉDIA"),
            _REC_RELEVANTE_PARA: o.get("relevant_for", _REC_DEFAULT_RELEVANTE),
        }
    return None


def _recommendation_row_for_pattern(pat: str, norm: str) -> dict:
    """
    Build a single recommendation row from pattern_detected and norm_tag.
    Priority: minor (Art. 14) > CPF/SSN/LGPD > EMAIL > CREDIT/CARD > default.
    """
    norm_lower = norm.lower()
    if "DOB_POSSIBLE_MINOR" in pat or ("LGPD Art. 14" in norm and ("menor" in norm_lower or "minor" in norm_lower)):
        return {
            _REC_DATA_PATTERN: pat,
            _REC_BASE_LEGAL: norm or "LGPD Art. 14 (dados de crianças/adolescentes); GDPR Art. 8 (consentimento em serviços da sociedade da informação)",
            _REC_RISCO: "Dados que podem se referir a menores de idade: tratamento sujeito a bases legais específicas, consentimento do titular ou dos pais/responsáveis e restrições de armazenamento, uso e compartilhamento.",
            _REC_RECOMENDACAO: (
                "Caso especial – dados de menores: (1) Garantir base legal e consentimento válido (titular ou responsável, conforme a idade e a lei aplicável). "
                "(2) Restringir armazenamento ao estritamente necessário; evitar retenção além do prazo. "
                "(3) Limitar uso e compartilhamento ao que for autorizado; não compartilhar com terceiros sem base legal e consentimento. "
                "(4) Revisar políticas de privacidade e termos para tratamento de dados de crianças/adolescentes (LGPD Art. 14; GDPR Art. 8). "
                "(5) Priorizar anonimização ou pseudonimização quando possível; controle de acesso rigoroso."
            ),
            _REC_PRIORIDADE: _REC_PRIORITY_CRITICA,
            _REC_RELEVANTE_PARA: "DPO, Compliance, Área jurídica, Segurança da Informação",
        }
    if "CPF" in pat or "SSN" in pat or "LGPD" in norm:
        return {
            _REC_DATA_PATTERN: pat,
            _REC_BASE_LEGAL: norm or "LGPD/GDPR – identificação direta",
            _REC_RISCO: "Identificação direta de pessoa natural (dados de cadastro/identidade).",
            _REC_RECOMENDACAO: "Anonimização ou hashing; restringir acesso (Least Privilege); revisar base legal e minimização.",
            _REC_PRIORIDADE: _REC_PRIORITY_CRITICA,
            _REC_RELEVANTE_PARA: "DPO, Segurança da Informação, Compliance",
        }
    if "EMAIL" in pat:
        return {
            _REC_DATA_PATTERN: pat,
            _REC_BASE_LEGAL: norm or "LGPD/GDPR – contato eletrônico",
            _REC_RISCO: "Vazamento de endereços de e-mail e possível uso indevido em campanhas/comunicações.",
            _REC_RECOMENDACAO: "Criptografia da coluna; revisão de logs de acesso; validação de consentimento e opt-out.",
            _REC_PRIORIDADE: "ALTA",
            _REC_RELEVANTE_PARA: "DPO, Marketing, Segurança da Informação",
        }
    if "CREDIT" in pat or "CARD" in pat:
        return {
            _REC_DATA_PATTERN: pat,
            _REC_BASE_LEGAL: norm or "LGPD/GDPR – dados financeiros / PCI-DSS",
            _REC_RISCO: "Fraude financeira, chargeback e exposição de dados de cartão/conta.",
            _REC_RECOMENDACAO: "Não armazenar número completo; tokenização; mascaramento; conformidade PCI-DSS e políticas internas.",
            _REC_PRIORIDADE: _REC_PRIORITY_CRITICA,
            _REC_RELEVANTE_PARA: "DPO, Segurança da Informação, Risco/Compliance financeiro",
        }
    return {
        _REC_DATA_PATTERN: pat,
        _REC_BASE_LEGAL: norm or "LGPD/GDPR/CCPA – dado pessoal ou sensível",
        _REC_RISCO: "Dado pessoal ou sensível com possível aumento de superfície de exposição.",
        _REC_RECOMENDACAO: "Avaliar necessidade do tratamento; aplicar pseudonimização ou criptografia; reforçar controle de acesso.",
        _REC_PRIORIDADE: "MÉDIA",
        _REC_RELEVANTE_PARA: _REC_DEFAULT_RELEVANTE,
    }


def _is_minor_recommendation_row(row: dict) -> bool:
    """True if row is a minor-related recommendation (for sorting)."""
    pat = (row.get(_REC_DATA_PATTERN) or "").strip()
    base = (row.get(_REC_BASE_LEGAL) or "").lower()
    return "DOB_POSSIBLE_MINOR" in pat or ("art. 14" in base and ("menor" in base or "minor" in base or "child" in base))


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
    seen: set[tuple[str, str]] = set()
    recs: list[dict] = []
    for r in db_rows + fs_rows:
        pat = r.get("pattern_detected") or ""
        norm = r.get("norm_tag") or ""
        if (pat, norm) in seen or not pat:
            continue
        seen.add((pat, norm))
        override_row = _find_override_row(pat, norm, overrides)
        if override_row is not None:
            recs.append(override_row)
            continue
        recs.append(_recommendation_row_for_pattern(pat, norm))
    if not recs:
        recs.append({
            _REC_DATA_PATTERN: "-",
            _REC_BASE_LEGAL: "-",
            _REC_RISCO: "Nenhum achado crítico nesta sessão",
            _REC_RECOMENDACAO: "Manter boas práticas de proteção de dados.",
            _REC_PRIORIDADE: "INFO",
            _REC_RELEVANTE_PARA: _REC_DEFAULT_RELEVANTE,
        })
    recs.sort(key=lambda r: (0 if _is_minor_recommendation_row(r) else 1, r.get(_REC_DATA_PATTERN, "")))
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
    prev_started_at = prev.get("started_at") if prev else None
    total_current = current_db + current_fs
    total_prev = (prev["database_findings"] + prev["filesystem_findings"]) if prev else None

    rows: list[dict] = []
    rows.append(_one_trend_row(
        _METRIC_TOTAL_FINDINGS, total_current, current_started_at,
        total_prev, prev_started_at, _METRIC_TOTAL_FINDINGS_LABEL,
    ))
    rows.append(_one_trend_row(
        _METRIC_DB_FINDINGS, current_db, current_started_at,
        prev.get("database_findings") if prev else None, prev_started_at, _METRIC_DB_FINDINGS,
    ))
    rows.append(_one_trend_row(
        _METRIC_FS_FINDINGS, current_fs, current_started_at,
        prev.get("filesystem_findings") if prev else None, prev_started_at, _METRIC_FS_FINDINGS,
    ))
    rows.append(_one_trend_row(
        _METRIC_SCAN_FAILURES, current_fail, current_started_at,
        prev.get("scan_failures") if prev else None, prev_started_at, _METRIC_SCAN_FAILURES_LABEL,
    ))
    return rows


def _get_session_metadata(db_manager: Any, session_id: str) -> dict[str, Any]:
    """Return started_at, tenant_name, technician_name, config_scope_hash for the given session (or None)."""
    for s in (db_manager.list_sessions() or []):
        if s.get("session_id") == session_id:
            return {
                "started_at": s.get("started_at"),
                "tenant_name": s.get("tenant_name"),
                "technician_name": s.get("technician_name"),
                "config_scope_hash": s.get("config_scope_hash"),
            }
    return {"started_at": None, "tenant_name": None, "technician_name": None, "config_scope_hash": None}


def _get_report_config_and_filtered_rows(
    config: dict | None,
    db_rows: list[dict],
    fs_rows: list[dict],
) -> tuple[dict, list[dict], list[dict]]:
    """Return (report_cfg, db_rows_for_sheets, fs_rows_for_sheets) with min_sensitivity applied."""
    cfg = config or {}
    report_cfg = cfg.get("report", {}) if isinstance(cfg.get("report"), dict) else {}
    min_sens = (report_cfg.get("min_sensitivity") or "LOW").upper()
    if min_sens != "LOW":
        return report_cfg, _filter_by_min_sensitivity(db_rows, min_sens), _filter_by_min_sensitivity(fs_rows, min_sens)
    return report_cfg, db_rows, fs_rows


def _build_executive_summary_rows(db_rows: list[dict], fs_rows: list[dict]) -> list[dict]:
    """Build rows for Executive summary sheet: by sensitivity, by norm_tag, top targets."""
    all_findings = db_rows + fs_rows
    exec_rows: list[dict] = []
    for level in ("HIGH", "MEDIUM", "LOW"):
        count = sum(1 for r in all_findings if (r.get("sensitivity_level") or "").upper() == level)
        exec_rows.append({"Metric": "Findings by sensitivity", "Category": level, "Count": count})
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
    for t, count in sorted(target_counts.items(), key=lambda x: -x[1])[:10]:
        exec_rows.append({"Metric": "Top targets by finding count", "Category": t, "Count": count})
    return exec_rows


def _apply_minor_confidence_and_return_keys(
    db_rows: list[dict],
    fs_rows: list[dict],
    config: dict | None,
) -> tuple[set[tuple], set[tuple]]:
    """
    If minor_cross_reference is enabled, compute high-confidence keys and set "Minor confidence" on rows; else clear it.
    Returns (db_high_keys, fs_high_keys) for use when prepending recommendation rows.
    """
    detection_cfg = (config or {}).get("detection") or {}
    if not detection_cfg.get("minor_cross_reference", True):
        for r in db_rows + fs_rows:
            r["Minor confidence"] = ""
        return set(), set()
    db_high_keys, fs_high_keys = _minor_cross_reference_confidence(db_rows, fs_rows)
    _apply_minor_confidence_column(
        db_rows, db_high_keys,
        lambda r: (r.get("target_name", ""), r.get("schema_name", ""), r.get("table_name", ""), r.get("column_name", "")),
    )
    _apply_minor_confidence_column(
        fs_rows, fs_high_keys,
        lambda r: (r.get("target_name", ""), r.get("path", ""), r.get("file_name", "")),
    )
    return db_high_keys, fs_high_keys


def _enrich_failures(fail_rows: list[dict]) -> list[dict]:
    """Add Category, Impact, Suggested next step to each failure row for the Scan failures sheet."""
    return [
        {
            **r,
            "Category": r.get("reason") or "error",
            "Impact": "Target was not fully scanned; overall coverage for this environment is incomplete until this issue is fixed.",
            "Suggested next step": failure_hint(r.get("reason") or "error"),
        }
        for r in fail_rows
    ]


def _write_excel_sheets(
    writer: Any,
    session_id: str,
    report_cfg: dict,
    db_rows_for_sheets: list[dict],
    fs_rows_for_sheets: list[dict],
    config: dict | None,
    fail_rows: list[dict],
    db_manager: Any,
    current_db: int,
    current_fs: int,
    current_fail: int,
    current_started_at: str | None,
    report_info: list[dict],
) -> None:
    """Write all Excel sheets (Report info, Executive summary, findings, recommendations, trends, heatmap data)."""
    pd.DataFrame(report_info).to_excel(writer, sheet_name="Report info", index=False)
    if report_cfg.get("include_executive_summary", False) and (db_rows_for_sheets or fs_rows_for_sheets):
        pd.DataFrame(_build_executive_summary_rows(db_rows_for_sheets, fs_rows_for_sheets)).to_excel(
            writer, sheet_name="Executive summary", index=False
        )
    db_high_keys, fs_high_keys = _apply_minor_confidence_and_return_keys(db_rows_for_sheets, fs_rows_for_sheets, config)
    if db_rows_for_sheets:
        pd.DataFrame(db_rows_for_sheets).to_excel(writer, sheet_name=_SHEET_DB_FINDINGS, index=False)
    if fs_rows_for_sheets:
        pd.DataFrame(fs_rows_for_sheets).to_excel(writer, sheet_name=_SHEET_FS_FINDINGS, index=False)
    agg_rows = db_manager.get_aggregated_identification_risks(session_id)
    if agg_rows:
        sheet_data = [
            {
                "Target": r.get("target_name", ""),
                "Source": r.get("source_type", ""),
                "Table / File": r.get("table_or_file", ""),
                "Columns involved": r.get("columns_involved", ""),
                "Categories": r.get("categories", ""),
                "Explanation": r.get("explanation", ""),
            }
            for r in agg_rows
        ]
        pd.DataFrame(sheet_data).to_excel(writer, sheet_name="Cross-ref data – ident. risk", index=False)
    if fail_rows:
        pd.DataFrame(_enrich_failures(fail_rows)).to_excel(writer, sheet_name=_SHEET_SCAN_FAILURES, index=False)
    overrides = report_cfg.get("recommendation_overrides", [])
    recs = _recommendations_rows(db_rows_for_sheets, fs_rows_for_sheets, recommendation_overrides=overrides if overrides else None)
    if agg_rows:
        recs.insert(0, {
            _REC_DATA_PATTERN: "AGGREGATED_IDENTIFICATION",
            _REC_BASE_LEGAL: "LGPD Art. 5 (dado pessoal); GDPR Recital 26 (identifiability – combination of data may identify individuals)",
            _REC_RISCO: "Dados de múltiplas colunas ou fontes (ex.: gênero, cargo, saúde, endereço, telefone) na mesma tabela/arquivo podem permitir identificação ou reidentificação de pessoas. Tratar como caso especial para DPO e compliance.",
            _REC_RECOMENDACAO: "Avaliar controles de acesso e limitação de finalidade; considerar anonimização ou pseudonimização; documentar base legal para o tratamento combinado (LGPD Art. 5; GDPR Recital 26).",
            _REC_PRIORIDADE: "ALTA",
            _REC_RELEVANTE_PARA: "DPO, Compliance, Segurança da Informação",
        })
    if db_high_keys or fs_high_keys:
        recs.insert(0, {
            _REC_DATA_PATTERN: "DOB_POSSIBLE_MINOR (high confidence – cross-ref)",
            _REC_BASE_LEGAL: "LGPD Art. 14 (dados de crianças/adolescentes); GDPR Art. 8 (consentimento em serviços da sociedade da informação)",
            _REC_RISCO: "Mesma tabela/arquivo contém data de nascimento sugerindo menor e dados identificadores ou de saúde; tratar como alta prioridade para DPO.",
            _REC_RECOMENDACAO: (
                "Caso especial – dados de menores: confirmar base legal e consentimento (titular ou responsável, conforme a idade e a lei aplicável); "
                "restringir acesso e retenção ao estritamente necessário; priorizar anonimização ou pseudonimização."
            ),
            _REC_PRIORIDADE: _REC_PRIORITY_CRITICA,
            _REC_RELEVANTE_PARA: "DPO, Compliance, Área jurídica, Segurança da Informação",
        })
    pd.DataFrame(recs).to_excel(writer, sheet_name="Recommendations", index=False)
    praise = _praise_rows(db_rows_for_sheets, fs_rows_for_sheets)
    if praise:
        pd.DataFrame(praise).to_excel(writer, sheet_name="Praise / existing controls", index=False)
    trends = _trends_rows(db_manager, session_id, current_db, current_fs, current_fail, current_started_at)
    pd.DataFrame(trends).to_excel(writer, sheet_name="Trends - Session comparison", index=False)
    heatmap_rows = [{"target": r.get("target_name"), "sensitivity": r.get("sensitivity_level")} for r in db_rows_for_sheets + fs_rows_for_sheets]
    if heatmap_rows:
        summary = pd.DataFrame(heatmap_rows).groupby(["target", "sensitivity"]).size().unstack(fill_value=0)
        summary.to_excel(writer, sheet_name="Heatmap data")


def _build_report_info(session_id: str, meta: dict, about: dict) -> list[dict]:
    """Build the Report info sheet rows (session + tenant/technician + about)."""
    report_info = [
        {"Field": "Session ID", "Value": session_id},
        {"Field": "Started at", "Value": meta["started_at"] or "—"},
        {"Field": "Tenant / Customer", "Value": meta["tenant_name"] or "—"},
        {"Field": "Technician / Operator", "Value": meta["technician_name"] or "—"},
    ]
    if meta.get("config_scope_hash"):
        report_info.append({"Field": "Config scope hash", "Value": meta["config_scope_hash"]})
    report_info.extend([
        {"Field": "Application", "Value": about["name"]},
        {"Field": "Version", "Value": about["version"]},
        {"Field": "Author", "Value": about["author"]},
        {"Field": "License", "Value": about["license"]},
        {"Field": "Copyright", "Value": about["copyright"]},
    ])
    return report_info


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
    if (config or {}).get("detection", {}).get("aggregated_identification_enabled", True):
        agg_records = run_aggregation(db_rows, fs_rows, session_id, config)
        db_manager.save_aggregated_identification_risks(session_id, agg_records)
    current_db = len(db_rows)
    current_fs = len(fs_rows)
    current_fail = len(fail_rows)
    report_cfg, db_rows_for_sheets, fs_rows_for_sheets = _get_report_config_and_filtered_rows(config, db_rows, fs_rows)
    meta = _get_session_metadata(db_manager, session_id)
    current_started_at = meta["started_at"]
    about = get_about_info()
    report_info = _build_report_info(session_id, meta, about)
    out_path = Path(output_dir) / f"Relatorio_Auditoria_{session_id[:16]}.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        _write_excel_sheets(
            writer, session_id, report_cfg, db_rows_for_sheets, fs_rows_for_sheets,
            config, fail_rows, db_manager, current_db, current_fs, current_fail,
            current_started_at, report_info,
        )
    _create_heatmap(db_rows_for_sheets, fs_rows_for_sheets, output_dir, session_id)
    return str(out_path)
