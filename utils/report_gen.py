"""Deprecated — legacy reporting helpers (FinOps + defensive-scanning hardening).

Active reporting path
---------------------
For new code, prefer:

- ``report.generator.generate_report`` — Excel report writer, sensitivity heatmap,
  trends sheet, recommendations.
- ``report.executive_report`` — executive Markdown with methodology and APG.
- ``report.recommendation_engine`` — structured mitigation plan (replaces the
  old in-line ``get_mitigation_plan`` here).

Why this module is deprecated
-----------------------------
The previous ``ReportGenerator.generate_comprehensive_report`` body executed:

    pd.read_sql("SELECT * FROM audit_findings", engine)

That single line violated three doctrines simultaneously:

1. **Defensive Scanning Manifesto** §2 — *no unbounded scans*. There was no
   ``LIMIT``, no projection, and no statement timeout. On a customer database
   with months of audit history this pulled every row and every column over
   the wire — direct cloud egress and memory bloat for nothing the report
   actually used.
2. **Defensive Scanning Manifesto** §4 — *DBA-grep contract*. The statement
   was emitted without the leading ``-- Data Boar Compliance Scan`` comment,
   so a DBA tailing activity views could not identify or kill it cleanly.
3. **The Art of the Fallback** §3 — *diagnostic on fall*. The query referred
   to a table (``audit_findings``) and columns (``target_name``,
   ``sensitivity_level``, ``pattern_detected``) that no longer exist in the
   current schema (see ``core/database.py``: ``database_findings`` and
   ``filesystem_findings``). Calling it would have raised ``OperationalError``
   silently from a worker — no audit row, no demoted strategy.

The module also failed to parse (``IndentationError`` on line 8 of the legacy
copy), which is why nothing in the active tree imported it. We are landing the
deprecation explicitly so the next reader gets a clear pointer instead of a
dormant landmine.

Removal plan
------------
Tracked via ``docs/plans/PLAN_ACTION_PLAN_GENERATOR_POST_SCAN.md`` (Phase A
hooks). Once the action-plan generator lands its own structured exporter,
this stub can be removed.
"""

from __future__ import annotations

import warnings
from typing import Any

import pandas as pd

__all__ = [
    "ReportGenerator",
    "create_risk_heatmap",
    "get_mitigation_plan",
]


_DEPRECATION_MSG = (
    "utils.report_gen is deprecated. Use report.generator.generate_report for "
    "Excel output and report.recommendation_engine for mitigation plans."
)


def _warn_deprecated(extra: str | None = None) -> None:
    msg = _DEPRECATION_MSG if not extra else f"{_DEPRECATION_MSG} {extra}"
    warnings.warn(msg, DeprecationWarning, stacklevel=3)


class ReportGenerator:
    """Deprecated stub — fail loud, never read the database.

    The previous implementation issued an unbounded ``SELECT * FROM
    audit_findings`` against the operator's database. We removed it on
    purpose: the cost of that pattern (full-table scan, no projection, no
    statement timeout, no DBA-grep comment) was higher than any value it
    delivered, and the active report pipeline lives in :mod:`report.generator`.

    Calling :meth:`generate_comprehensive_report` raises
    :class:`NotImplementedError` so we **never** silently fall back into a
    weaker, costlier path — see ``THE_ART_OF_THE_FALLBACK.md`` §3.
    """

    def __init__(self, db_manager: Any) -> None:
        self.db_manager = db_manager
        _warn_deprecated()

    def generate_comprehensive_report(self) -> None:  # pragma: no cover - guard
        raise NotImplementedError(
            "utils.report_gen.ReportGenerator was retired to remove an "
            "unbounded 'SELECT * FROM audit_findings' read. Use "
            "report.generator.generate_report(local_db_manager, ...) instead."
        )


def create_risk_heatmap(df: pd.DataFrame) -> None:  # pragma: no cover - guard
    """Deprecated — use ``report.generator`` heatmap helpers."""
    _warn_deprecated("Heatmaps are produced by report.generator.")
    raise NotImplementedError(
        "utils.report_gen.create_risk_heatmap is retired. "
        "Use report.generator.generate_report which writes the heatmap as "
        "part of the canonical Excel output."
    )


def get_mitigation_plan(findings_df: pd.DataFrame) -> pd.DataFrame:
    """Pure-Python mitigation summary kept for backwards compatibility.

    This helper does **not** touch the database — it consumes a caller-owned
    DataFrame of findings and groups recommendations by ``pattern_detected``.
    Kept so legacy notebooks and the action-plan generator (Phase A in
    ``PLAN_ACTION_PLAN_GENERATOR_POST_SCAN.md``) can continue to import it
    while we migrate to :mod:`report.recommendation_engine`.

    Parameters
    ----------
    findings_df:
        Pandas DataFrame with at least a ``pattern_detected`` column.

    Returns
    -------
    pandas.DataFrame
        One row per unique violation with localized risk / action /
        priority columns. Empty DataFrame if the input has no findings or
        no ``pattern_detected`` column.
    """

    _warn_deprecated(
        "Use report.recommendation_engine.RecommendationEngine for "
        "structured mitigation rows."
    )

    if findings_df is None or len(findings_df) == 0:
        return pd.DataFrame(
            columns=["Violação", "Risco", "Ação Recomendada", "Prioridade"]
        )
    if "pattern_detected" not in findings_df.columns:
        return pd.DataFrame(
            columns=["Violação", "Risco", "Ação Recomendada", "Prioridade"]
        )

    recommendations: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_violation in findings_df["pattern_detected"].dropna().unique():
        violation = str(raw_violation)
        if not violation or violation in seen:
            continue
        seen.add(violation)

        upper = violation.upper()
        if "CPF" in upper or "SSN" in upper:
            recommendations.append(
                {
                    "Violação": violation,
                    "Risco": "Identificação direta de pessoa natural (alta severidade)",
                    "Ação Recomendada": (
                        "Aplicar técnicas de anonimização ou hashing. "
                        "Restringir acesso ao mínimo necessário (least privilege)."
                    ),
                    "Prioridade": "CRÍTICA",
                }
            )
        elif "EMAIL" in upper:
            recommendations.append(
                {
                    "Violação": violation,
                    "Risco": "Comunicação não autorizada ou vazamento de base de marketing",
                    "Ação Recomendada": (
                        "Criptografia da coluna de e-mail e revisão de logs de acesso (auditoria)."
                    ),
                    "Prioridade": "ALTA",
                }
            )
        elif "ML_DETECTED" in upper:
            recommendations.append(
                {
                    "Violação": "Identificado via Machine Learning",
                    "Risco": "Contexto sugere dados sensíveis não estruturados",
                    "Ação Recomendada": (
                        "Revisão manual por analista de privacidade e classificação formal do banco de dados."
                    ),
                    "Prioridade": "MÉDIA",
                }
            )

    return pd.DataFrame(recommendations)
