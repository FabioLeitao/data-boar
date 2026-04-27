"""
DPO / CISO Action Plan — Board-ready Executive Summary layer (APG Phase B).

Purpose
-------
Transform Phase-A APG rows (``pattern → action``) into a *Remediation Roadmap* a
DPO or CISO can take to a board meeting:

1. **Legal mapping** — every pattern is paired with the LGPD / GDPR articles that
   plausibly govern it (workshop hint, **not** legal advice — DPO validates per
   engagement, mirroring the disclaimer in :mod:`core.intelligence`).
2. **Highest-leverage remediation** — collapses the verbose APG ``action`` text
   into a single canonical verb (``Anonymize``, ``Encrypt``, ``Tokenize``,
   ``Pseudonymize``, ``Mask``, ``Delete``, ``Review``) so the board sees *what
   to do* before *how to do it*.
3. **Risk Heatmap** — composite ``Data Sensitivity × DB Exposure × Access Level``
   score (0..100) projected onto a four-tier criticality band so the DPO can
   prioritize the next 30 days of remediation work.

Doctrinal anchors
-----------------
- ``docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`` — this module is a
  **read-only post-processor** over already-collected metadata. It performs
  **zero** database I/O, opens **zero** transactions, and never widens the
  customer's lock footprint. Composition only.
- ``docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`` — unknown patterns and
  empty inputs degrade gracefully to a "Review" verb and a documented neutral
  band; we never raise on a malformed APG row.
- ``docs/ops/inspirations/ACTIONABLE_GOVERNANCE_AND_TRUST.md`` — the executive
  Markdown is a *path to the cure*; this module supplies the cure verbs and the
  legal article every claim leans on.

The module exposes pure functions; rendering helpers return Markdown line lists
so the caller (``report.executive_report``) controls section ordering.
"""

from __future__ import annotations

from typing import Any, Iterable, Literal, Mapping, Sequence

from core.intelligence import classify_pii_category, normalize_pii_type_key
from core.recommendations import apg_priority

# Canonical remediation verbs, ordered from "stronger guarantee" to "weaker".
# The board-ready summary speaks in these verbs only — APG prose stays in §4.2.
RemediationVerb = Literal[
    "Tokenize",
    "Encrypt",
    "Anonymize",
    "Pseudonymize",
    "Mask",
    "Delete",
    "Review",
]

# Criticality band for the heatmap. Ordered ascending (low → high).
CriticalityBand = Literal["Baixa", "Média", "Alta", "Crítica"]

# 0..100 thresholds for criticality bands. Tuned so a single ``CREDIT_CARD``
# finding with default exposure already lands in "Crítica" (PCI must surface).
_CRITICALITY_THRESHOLDS: tuple[tuple[float, CriticalityBand], ...] = (
    (75.0, "Crítica"),
    (60.0, "Alta"),
    (35.0, "Média"),
    (0.0, "Baixa"),
)

# Pattern → LGPD / GDPR article hints. Workshop-grade; DPO confirms per case.
# Keys are normalized via :func:`core.intelligence.normalize_pii_type_key`.
_LEGAL_ARTICLES_BY_PATTERN: dict[str, dict[str, tuple[str, ...]]] = {
    "CPF": {
        "lgpd": ("Art. 5, I", "Art. 7", "Art. 46"),
        "gdpr": ("Art. 6", "Art. 32"),
    },
    "LGPD_CPF": {
        "lgpd": ("Art. 5, I", "Art. 7", "Art. 46"),
        "gdpr": ("Art. 6", "Art. 32"),
    },
    "CNPJ": {
        "lgpd": ("Art. 7",),
        "gdpr": ("Art. 6",),
    },
    "LGPD_CNPJ": {
        "lgpd": ("Art. 7",),
        "gdpr": ("Art. 6",),
    },
    "LGPD_CNPJ_ALNUM": {
        "lgpd": ("Art. 7",),
        "gdpr": ("Art. 6",),
    },
    "CREDIT_CARD": {
        "lgpd": ("Art. 46", "Art. 49"),
        "gdpr": ("Art. 32", "Art. 5(1)(f)"),
    },
    "EMAIL": {
        "lgpd": ("Art. 5, I", "Art. 6"),
        "gdpr": ("Art. 5(1)(c)", "Art. 6"),
    },
    "PHONE_BR": {
        "lgpd": ("Art. 5, I", "Art. 6"),
        "gdpr": ("Art. 5(1)(c)", "Art. 6"),
    },
    "SSN": {
        "lgpd": ("Art. 5, I", "Art. 46"),
        "gdpr": ("Art. 6", "Art. 32"),
    },
    "CCPA_SSN": {
        "lgpd": ("Art. 5, I", "Art. 46"),
        "gdpr": ("Art. 6", "Art. 32"),
    },
    "DATE_DMY": {
        "lgpd": ("Art. 6",),
        "gdpr": ("Art. 5(1)(c)", "Art. 5(1)(e)"),
    },
}

# Coarse RiskCategory → fallback legal hints when the pattern is unknown but
# classifiable. Mirrors :data:`core.intelligence.LAW_MAPPING` but split by
# regulation so the DPO summary can tag both columns.
_LEGAL_ARTICLES_BY_CATEGORY: dict[str, dict[str, tuple[str, ...]]] = {
    "FINANCIAL": {
        "lgpd": ("Art. 7", "Art. 46"),
        "gdpr": ("Art. 6", "Art. 32"),
    },
    "SENSITIVE": {
        "lgpd": ("Art. 11", "Art. 5, II"),
        "gdpr": ("Art. 9",),
    },
    "CHILD_DATA": {
        "lgpd": ("Art. 14",),
        "gdpr": ("Art. 8",),
    },
    "IDENTIFIER": {
        "lgpd": ("Art. 5, I",),
        "gdpr": ("Art. 5(1)(c)", "Art. 6"),
    },
}

# Pattern → highest-leverage remediation verb. The verb is the *strongest*
# control that still preserves business utility; downstream prose may add
# qualifiers (e.g. "tokenization plus log isolation").
_REMEDIATION_VERB_BY_PATTERN: dict[str, RemediationVerb] = {
    "CREDIT_CARD": "Tokenize",
    "CPF": "Encrypt",
    "LGPD_CPF": "Encrypt",
    "SSN": "Encrypt",
    "CCPA_SSN": "Encrypt",
    "CNPJ": "Mask",
    "LGPD_CNPJ": "Mask",
    "LGPD_CNPJ_ALNUM": "Mask",
    "EMAIL": "Pseudonymize",
    "PHONE_BR": "Pseudonymize",
    "DATE_DMY": "Review",
    "GENERIC_PII": "Review",
}

# Coarse RiskCategory → verb fallback when the pattern is unknown. Keeps the
# board summary aligned with the dominant risk class even for new detectors.
_REMEDIATION_VERB_BY_CATEGORY: dict[str, RemediationVerb] = {
    "FINANCIAL": "Encrypt",
    "SENSITIVE": "Anonymize",
    "CHILD_DATA": "Delete",
    "IDENTIFIER": "Pseudonymize",
}

# Per-pattern data-sensitivity weight (0..100). Anchors the heatmap so that a
# single PCI finding still ranks above a hundred low-sensitivity rows. Tuned
# against :func:`core.recommendations.apg_priority` (lower priority -> higher
# weight) and the LGPD-aligned weights in :mod:`core.intelligence`.
_SENSITIVITY_WEIGHT_BY_PATTERN: dict[str, float] = {
    "CREDIT_CARD": 100.0,
    "CCPA_SSN": 95.0,
    "SSN": 95.0,
    "CPF": 90.0,
    "LGPD_CPF": 90.0,
    "CNPJ": 70.0,
    "LGPD_CNPJ": 70.0,
    "LGPD_CNPJ_ALNUM": 70.0,
    "EMAIL": 50.0,
    "PHONE_BR": 50.0,
    "DATE_DMY": 35.0,
    "GENERIC_PII": 25.0,
}


def _normalize_pattern(pattern: str | None) -> str:
    """Uppercase + strip helper that tolerates ``None`` from APG rows."""
    return normalize_pii_type_key(pattern or "")


def legal_articles_for_pattern(pattern: str) -> dict[str, tuple[str, ...]]:
    """
    Return ``{"lgpd": (...), "gdpr": (...)}`` article hints for ``pattern``.

    Falls back to the dominant :class:`RiskCategory` mapping when the pattern is
    not in the canonical table — graceful degradation per
    ``THE_ART_OF_THE_FALLBACK.md`` (we never return an empty tuple for a real
    finding; ``GENERIC_PII`` and friends still get the IDENTIFIER hints).
    """
    key = _normalize_pattern(pattern)
    if key in _LEGAL_ARTICLES_BY_PATTERN:
        block = _LEGAL_ARTICLES_BY_PATTERN[key]
        return {"lgpd": tuple(block["lgpd"]), "gdpr": tuple(block["gdpr"])}
    if not key:
        return {"lgpd": (), "gdpr": ()}
    category = classify_pii_category(key)
    block = _LEGAL_ARTICLES_BY_CATEGORY.get(
        category, _LEGAL_ARTICLES_BY_CATEGORY["IDENTIFIER"]
    )
    return {"lgpd": tuple(block["lgpd"]), "gdpr": tuple(block["gdpr"])}


def highest_leverage_remediation(pattern: str) -> RemediationVerb:
    """
    Map ``pattern`` to a single canonical remediation verb.

    The verb is the **strongest** control that still preserves business utility
    for that data class. Used in the board-ready summary; the verbose APG prose
    in §4.2 keeps the operational nuance (e.g. tokenization *and* log isolation
    for PCI).
    """
    key = _normalize_pattern(pattern)
    if key in _REMEDIATION_VERB_BY_PATTERN:
        return _REMEDIATION_VERB_BY_PATTERN[key]
    if not key:
        return "Review"
    category = classify_pii_category(key)
    return _REMEDIATION_VERB_BY_CATEGORY.get(category, "Review")


def _sensitivity_weight(pattern: str) -> float:
    """Per-pattern sensitivity weight (0..100). Unknown patterns get a neutral 30."""
    key = _normalize_pattern(pattern)
    if key in _SENSITIVITY_WEIGHT_BY_PATTERN:
        return _SENSITIVITY_WEIGHT_BY_PATTERN[key]
    if not key:
        return 0.0
    category = classify_pii_category(key)
    if category == "CHILD_DATA":
        return 100.0
    if category == "SENSITIVE":
        return 80.0
    if category == "FINANCIAL":
        return 70.0
    return 30.0


def _clamp(value: float, *, low: float = 0.0, high: float = 100.0) -> float:
    """Clamp helper — defensive scanning posture: never emit a > 100 score."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def compute_criticality_score(
    pattern: str,
    finding_count: int,
    *,
    exposure_factor: float = 1.0,
    access_factor: float = 1.0,
) -> float:
    """
    Composite ``Data Sensitivity × DB Exposure × Access Level`` score (0..100).

    - **Data Sensitivity** comes from :func:`_sensitivity_weight` (0..100).
    - **DB Exposure** is a logarithmic boost on ``finding_count`` so a single
      finding still surfaces (no zero), but a thousand findings does not blow
      the scale: ``min(1.5, 1.0 + log10(max(1, count)) / 4)``.
    - **Access Level** is operator-supplied (default 1.0). Callers may pass
      lower values for restricted assets and higher values for asset rows
      flagged as broadly accessible — the heatmap respects what the engagement
      knows; we never invent that signal.

    Returns a float clamped to ``[0, 100]``.
    """
    from math import log10

    sensitivity = _sensitivity_weight(pattern)
    if sensitivity <= 0.0:
        return 0.0
    safe_count = max(1, int(finding_count or 0))
    exposure_boost = 1.0 + (log10(float(safe_count)) / 4.0)
    exposure_boost = min(1.5, exposure_boost)
    raw = sensitivity * exposure_boost * float(exposure_factor) * float(access_factor)
    return round(_clamp(raw), 2)


def criticality_band(score: float) -> CriticalityBand:
    """Map a 0..100 score to a four-tier criticality label."""
    safe_score = float(score or 0.0)
    for threshold, band in _CRITICALITY_THRESHOLDS:
        if safe_score >= threshold:
            return band
    return "Baixa"


def _format_articles(articles: Sequence[str]) -> str:
    """Render an article tuple as ``Art. 6 / Art. 32`` for inline prose."""
    return " / ".join(articles) if articles else "—"


def build_dpo_action_plan(
    apg_rows: Sequence[Mapping[str, Any]],
    *,
    exposure_factor: float = 1.0,
    access_factor: float = 1.0,
) -> dict[str, Any]:
    """
    Build the structured DPO/CISO action-plan payload from APG rows.

    The payload is the single source of truth for the Markdown renderer — it
    keeps prose and data aligned, and lets future surfaces (HTML, PDF, JSON
    export) consume the same fields.

    Parameters
    ----------
    apg_rows
        Aggregated APG rows. Same shape consumed by
        :func:`report.executive_report.generate_executive_report` —
        ``pattern_detected``, ``finding_count``, ``recommended_action``, etc.
    exposure_factor, access_factor
        Per-engagement multipliers (default ``1.0``). The orchestration layer
        may pass tuned values when the engagement knows the asset is broadly
        exposed (e.g. unauthenticated read endpoint) or narrowly scoped.

    Returns
    -------
    dict
        Keys: ``executive_summary`` (str), ``heatmap_rows`` (list of dicts),
        ``thirty_day_priorities`` (list of dicts), ``criticality_counts``
        (Counter-like dict).
    """
    safe_rows = [row for row in apg_rows or () if isinstance(row, Mapping)]
    enriched: list[dict[str, Any]] = []
    for row in safe_rows:
        pattern = str(row.get("pattern_detected") or "").strip()
        if not pattern:
            continue
        try:
            finding_count = int(row.get("finding_count") or 0)
        except (TypeError, ValueError):
            # Doctrine: malformed inputs degrade — they do not crash the report.
            # See docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md.
            finding_count = 0
        score = compute_criticality_score(
            pattern,
            finding_count,
            exposure_factor=exposure_factor,
            access_factor=access_factor,
        )
        band = criticality_band(score)
        articles = legal_articles_for_pattern(pattern)
        verb = highest_leverage_remediation(pattern)
        enriched.append(
            {
                "pattern": pattern,
                "finding_count": finding_count,
                "criticality_score": score,
                "criticality_band": band,
                "remediation_verb": verb,
                "lgpd_articles": articles["lgpd"],
                "gdpr_articles": articles["gdpr"],
                "apg_priority": apg_priority(pattern),
            }
        )

    enriched.sort(
        key=lambda r: (
            -float(r["criticality_score"]),
            int(r["apg_priority"]),
            -int(r["finding_count"]),
            str(r["pattern"]),
        )
    )

    counts: dict[CriticalityBand, int] = {
        "Crítica": 0,
        "Alta": 0,
        "Média": 0,
        "Baixa": 0,
    }
    for row in enriched:
        counts[row["criticality_band"]] += 1

    thirty_day = [r for r in enriched if r["criticality_band"] in ("Crítica", "Alta")]
    if not thirty_day:
        thirty_day = enriched[:3]

    summary = _build_executive_summary_sentence(enriched, counts)
    return {
        "executive_summary": summary,
        "heatmap_rows": enriched,
        "thirty_day_priorities": thirty_day,
        "criticality_counts": dict(counts),
    }


def _build_executive_summary_sentence(
    enriched: Sequence[Mapping[str, Any]],
    counts: Mapping[CriticalityBand, int],
) -> str:
    """One-paragraph plain-language summary the board can read in 15 seconds."""
    if not enriched:
        return (
            "Nesta sessão a varredura não catalogou tipos de dados pessoais "
            "elegíveis para plano de ação executivo. Reexecute com alvos "
            "configurados antes da próxima reunião com o DPO."
        )
    total_patterns = len(enriched)
    crit = counts.get("Crítica", 0)
    high = counts.get("Alta", 0)
    top = enriched[0]
    top_pattern = str(top["pattern"])
    top_band = str(top["criticality_band"])
    top_verb = str(top["remediation_verb"])
    if crit:
        urgency = (
            f"{crit} tipo(s) em criticidade **Crítica** exigem ação imediata "
            "(janela de 30 dias)"
        )
    elif high:
        urgency = (
            f"{high} tipo(s) em criticidade **Alta** devem entrar no roteiro "
            "do próximo ciclo de remediação"
        )
    else:
        urgency = "nenhum tipo atinge criticidade Alta ou Crítica nesta sessão"
    return (
        f"Foram catalogados **{total_patterns}** tipos de dados pessoais; "
        f"{urgency}. O tipo mais sensível (`{top_pattern}`, criticidade "
        f"**{top_band}**) tem como remediação de maior alavancagem **{top_verb}**. "
        "Este resumo não substitui parecer jurídico — o DPO valida o "
        "enquadramento em LGPD/GDPR antes da execução."
    )


def render_dpo_action_plan_md(payload: Mapping[str, Any]) -> list[str]:
    """
    Render the DPO action plan as Markdown lines (no trailing newline).

    The caller is responsible for inserting the section header and weaving the
    output into the larger executive report; this function returns *only* the
    body so it stays composable with other Board-ready surfaces.
    """
    lines: list[str] = []
    summary: str = str(payload.get("executive_summary") or "")
    if summary:
        lines.extend(["**Resumo executivo (DPO/CISO):**", "", summary, ""])

    heatmap = list(payload.get("heatmap_rows") or [])
    counts = dict(payload.get("criticality_counts") or {})
    if heatmap:
        lines.extend(
            [
                "**Heatmap de criticidade — `Sensibilidade × Exposição × Nível de acesso`:**",
                "",
                f"- Crítica: **{counts.get('Crítica', 0)}** · "
                f"Alta: **{counts.get('Alta', 0)}** · "
                f"Média: **{counts.get('Média', 0)}** · "
                f"Baixa: **{counts.get('Baixa', 0)}**",
                "",
                "| Tipo | Achados | Criticidade | Score | Remediação | LGPD | GDPR |",
                "| ---- | ------- | ----------- | ----- | ---------- | ---- | ---- |",
            ]
        )
        for row in heatmap:
            pattern = str(row.get("pattern") or "—")
            count = int(row.get("finding_count") or 0)
            band = str(row.get("criticality_band") or "—")
            score = float(row.get("criticality_score") or 0.0)
            verb = str(row.get("remediation_verb") or "Review")
            lgpd = _format_articles(tuple(row.get("lgpd_articles") or ()))
            gdpr = _format_articles(tuple(row.get("gdpr_articles") or ()))
            lines.append(
                f"| `{pattern}` | {count} | **{band}** | {score:.1f} | {verb} | {lgpd} | {gdpr} |"
            )
        lines.append("")

    thirty_day = list(payload.get("thirty_day_priorities") or [])
    if thirty_day:
        lines.extend(
            [
                "**Prioridades para os próximos 30 dias:**",
                "",
            ]
        )
        for idx, row in enumerate(thirty_day, start=1):
            pattern = str(row.get("pattern") or "—")
            band = str(row.get("criticality_band") or "—")
            verb = str(row.get("remediation_verb") or "Review")
            lgpd = _format_articles(tuple(row.get("lgpd_articles") or ()))
            lines.append(
                f"{idx}. **`{pattern}`** — criticidade **{band}**: aplicar "
                f"**{verb}** (LGPD {lgpd})."
            )
        lines.append("")

    return lines


def collect_unique_patterns(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    """Helper: deduplicate ``pattern_detected`` while preserving first-seen order."""
    seen: set[str] = set()
    ordered: list[str] = []
    for row in rows or ():
        if not isinstance(row, Mapping):
            continue
        pattern = _normalize_pattern(str(row.get("pattern_detected") or ""))
        if not pattern or pattern in seen:
            continue
        seen.add(pattern)
        ordered.append(pattern)
    return ordered


__all__ = [
    "CriticalityBand",
    "RemediationVerb",
    "build_dpo_action_plan",
    "collect_unique_patterns",
    "compute_criticality_score",
    "criticality_band",
    "highest_leverage_remediation",
    "legal_articles_for_pattern",
    "render_dpo_action_plan_md",
]
