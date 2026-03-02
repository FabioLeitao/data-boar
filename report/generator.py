"""
Single report generator: reads database_findings, filesystem_findings, scan_failures from LocalDBManager
for a session; produces Excel with sheets "Database findings", "Filesystem findings", "Scan failures",
"Recommendations", and heatmap image (sensitivity/risk). Returns path to Excel file.
"""
from pathlib import Path
from typing import Any

import pandas as pd

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
    """Build sensitivity/risk heatmap; save PNG. Return path or None."""
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


def _recommendations_rows(db_rows: list[dict], fs_rows: list[dict]) -> list[dict]:
    """Build recommendations from unique pattern_detected and norm_tag."""
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
                "Base legal": norm,
                "Risco": "Identificação direta de pessoa natural",
                "Recomendação": "Anonimização ou hashing; restringir acesso (Least Privilege).",
                "Prioridade": "CRÍTICA",
            })
        elif "EMAIL" in pat:
            recs.append({
                "Data / Pattern": pat,
                "Base legal": norm,
                "Risco": "Vazamento de comunicação / marketing",
                "Recomendação": "Criptografia da coluna; revisão de logs de acesso.",
                "Prioridade": "ALTA",
            })
        elif "CREDIT" in pat or "CARD" in pat:
            recs.append({
                "Data / Pattern": pat,
                "Base legal": norm,
                "Risco": "Fraude financeira / PCI",
                "Recomendação": "Não armazenar número completo; tokenização; conformidade PCI-DSS.",
                "Prioridade": "CRÍTICA",
            })
        else:
            recs.append({
                "Data / Pattern": pat,
                "Base legal": norm,
                "Risco": "Dado pessoal ou sensível (LGPD/GDPR/CCPA)",
                "Recomendação": "Avaliar necessidade; pseudonimização ou criptografia; controle de acesso.",
                "Prioridade": "MÉDIA",
            })
    if not recs:
        recs.append({
            "Data / Pattern": "-",
            "Base legal": "-",
            "Risco": "Nenhum achado crítico nesta sessão",
            "Recomendação": "Manter boas práticas de proteção de dados.",
            "Prioridade": "INFO",
        })
    return recs


def generate_report(db_manager: Any, session_id: str, output_dir: str = ".") -> str | None:
    """
    Read session from db_manager (database_findings, filesystem_findings, scan_failures);
    write Excel and heatmap. Return path to Excel file or None.
    """
    db_rows, fs_rows, fail_rows = db_manager.get_findings(session_id)
    if not db_rows and not fs_rows and not fail_rows:
        return None
    out_path = Path(output_dir) / f"Relatorio_Auditoria_{session_id[:16]}.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        if db_rows:
            pd.DataFrame(db_rows).to_excel(writer, sheet_name="Database findings", index=False)
        if fs_rows:
            pd.DataFrame(fs_rows).to_excel(writer, sheet_name="Filesystem findings", index=False)
        if fail_rows:
            pd.DataFrame(fail_rows).to_excel(writer, sheet_name="Scan failures", index=False)
        recs = _recommendations_rows(db_rows, fs_rows)
        pd.DataFrame(recs).to_excel(writer, sheet_name="Recommendations", index=False)
        # Summary heatmap data as sheet
        rows = [{"target": r.get("target_name"), "sensitivity": r.get("sensitivity_level")} for r in db_rows + fs_rows]
        if rows:
            summary = pd.DataFrame(rows).groupby(["target", "sensitivity"]).size().unstack(fill_value=0)
            summary.to_excel(writer, sheet_name="Heatmap data")
    _create_heatmap(db_rows, fs_rows, output_dir, session_id)
    return str(out_path)
