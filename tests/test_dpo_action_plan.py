"""DPO / CISO Action Plan layer (legal mapping + heatmap + verbs)."""

from __future__ import annotations

from report.dpo_action_plan import (
    build_dpo_action_plan,
    compute_criticality_score,
    criticality_band,
    highest_leverage_remediation,
    legal_articles_for_pattern,
    render_dpo_action_plan_md,
)


def test_legal_articles_for_known_patterns_include_lgpd_and_gdpr() -> None:
    cc = legal_articles_for_pattern("CREDIT_CARD")
    assert cc["lgpd"] and cc["gdpr"]
    assert any("Art. 46" in a or "Art. 49" in a for a in cc["lgpd"])

    cpf = legal_articles_for_pattern("CPF")
    assert "Art. 5, I" in cpf["lgpd"]
    assert any(a.startswith("Art. ") for a in cpf["gdpr"])


def test_legal_articles_unknown_pattern_falls_back_to_category() -> None:
    """Unknown labels degrade gracefully; we never silently drop the row."""
    out = legal_articles_for_pattern("HEALTH_RECORD")
    assert out["lgpd"] and out["gdpr"]
    assert any("Art. 11" in a or "Art. 9" in a for a in out["lgpd"] + out["gdpr"])


def test_legal_articles_empty_pattern_returns_empty_tuples() -> None:
    out = legal_articles_for_pattern("")
    assert out == {"lgpd": (), "gdpr": ()}


def test_highest_leverage_verb_per_pattern() -> None:
    assert highest_leverage_remediation("CREDIT_CARD") == "Tokenize"
    assert highest_leverage_remediation("CPF") == "Encrypt"
    assert highest_leverage_remediation("EMAIL") == "Pseudonymize"
    assert highest_leverage_remediation("LGPD_CNPJ") == "Mask"
    assert highest_leverage_remediation("DATE_DMY") == "Review"


def test_highest_leverage_verb_unknown_uses_category_fallback() -> None:
    assert highest_leverage_remediation("HEALTH_RECORD") == "Anonymize"
    assert highest_leverage_remediation("DOB_POSSIBLE_MINOR") == "Delete"
    assert highest_leverage_remediation("") == "Review"


def test_criticality_score_credit_card_lands_in_critica_band() -> None:
    score = compute_criticality_score("CREDIT_CARD", finding_count=1)
    assert score >= 75.0
    assert criticality_band(score) == "Crítica"


def test_criticality_score_email_low_volume_is_media_or_baixa() -> None:
    score = compute_criticality_score("EMAIL", finding_count=2)
    band = criticality_band(score)
    assert band in {"Baixa", "Média"}


def test_criticality_score_clamped_to_100() -> None:
    score = compute_criticality_score(
        "CREDIT_CARD",
        finding_count=10_000_000,
        exposure_factor=5.0,
        access_factor=5.0,
    )
    assert score <= 100.0


def test_criticality_score_zero_for_empty_pattern() -> None:
    assert compute_criticality_score("", finding_count=10) == 0.0


def test_build_payload_orders_critica_first_and_counts_bands() -> None:
    apg_rows = [
        {"pattern_detected": "EMAIL", "finding_count": 3},
        {"pattern_detected": "CREDIT_CARD", "finding_count": 1},
        {"pattern_detected": "CPF", "finding_count": 5},
    ]
    payload = build_dpo_action_plan(apg_rows)
    rows = payload["heatmap_rows"]
    assert rows[0]["pattern"] == "CREDIT_CARD"
    assert rows[0]["criticality_band"] == "Crítica"
    counts = payload["criticality_counts"]
    assert counts["Crítica"] >= 1
    assert sum(counts.values()) == len(rows)


def test_build_payload_thirty_day_priorities_prefers_critica_alta() -> None:
    apg_rows = [
        {"pattern_detected": "EMAIL", "finding_count": 1},
        {"pattern_detected": "CREDIT_CARD", "finding_count": 1},
    ]
    payload = build_dpo_action_plan(apg_rows)
    priorities = payload["thirty_day_priorities"]
    assert priorities, "expected at least one 30-day priority"
    assert priorities[0]["pattern"] == "CREDIT_CARD"


def test_build_payload_empty_input_returns_neutral_summary() -> None:
    payload = build_dpo_action_plan([])
    assert payload["heatmap_rows"] == []
    assert "reexecute" in payload["executive_summary"].lower()


def test_build_payload_skips_malformed_rows_without_raising() -> None:
    """Fallback contract: malformed rows degrade, never crash the report."""
    apg_rows = [
        {"pattern_detected": ""},
        None,  # type: ignore[list-item]
        {"pattern_detected": "EMAIL", "finding_count": "not-an-int"},
        {"pattern_detected": "CPF", "finding_count": 2},
    ]
    payload = build_dpo_action_plan(apg_rows)  # type: ignore[arg-type]
    patterns = [r["pattern"] for r in payload["heatmap_rows"]]
    assert "CPF" in patterns
    assert "EMAIL" in patterns


def test_render_dpo_action_plan_md_emits_table_and_summary() -> None:
    apg_rows = [
        {"pattern_detected": "CREDIT_CARD", "finding_count": 2},
        {"pattern_detected": "EMAIL", "finding_count": 4},
    ]
    payload = build_dpo_action_plan(apg_rows)
    md_lines = render_dpo_action_plan_md(payload)
    md = "\n".join(md_lines)
    assert "Resumo executivo (DPO/CISO)" in md
    assert "Heatmap de criticidade" in md
    assert "| Tipo |" in md
    assert "Tokenize" in md  # highest-leverage verb for CREDIT_CARD
    assert "LGPD" in md and "GDPR" in md
    assert "Prioridades para os próximos 30 dias" in md
    # Sanitization: the renderer must not echo finding-row objects, only patterns.
    assert "{'" not in md


def test_render_dpo_action_plan_md_empty_payload() -> None:
    payload = build_dpo_action_plan([])
    md = "\n".join(render_dpo_action_plan_md(payload))
    assert "Resumo executivo" in md
    assert "Heatmap" not in md  # no table when no rows
