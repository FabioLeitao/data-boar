"""
Relatório de mesa — Markdown executivo (mitigação de risco, sem detalhe de código).

Usa :func:`core.advisor.group_findings_by_risk` e o ranking APG de ``core.recommendations``.
"""

from __future__ import annotations

from typing import Any

from core.advisor import group_findings_by_risk
from report.dpo_action_plan import build_dpo_action_plan, render_dpo_action_plan_md
from report.recommendation_engine import sort_apg_rows, top_n_recommendations
from report.safe_prefix import safe_session_prefix


def _executive_status_emoji_and_label(
    db_rows: list[dict],
    apg_rows: list[dict[str, Any]],
    filesystem_findings: int,
) -> tuple[str, str]:
    critical_patterns = {
        "CREDIT_CARD",
        "LGPD_CPF",
        "CPF",
        "CCPA_SSN",
        "SSN",
        "LGPD_CNPJ",
        "LGPD_CNPJ_ALNUM",
        "CNPJ",
    }
    patterns = {(r.get("pattern_detected") or "").strip().upper() for r in db_rows}
    high_sens = any(
        (r.get("sensitivity_level") or "").strip().upper() == "HIGH" for r in db_rows
    )
    if patterns & critical_patterns or high_sens:
        return (
            "🔴",
            "Risco elevado detectado (dados sensíveis / PCI / identificadores fortes).",
        )
    crit_from_apg = any(
        (r.get("pattern_detected") or "").upper() in critical_patterns
        or "Bloqueante" in str(r.get("risk_band", ""))
        for r in apg_rows
    )
    if crit_from_apg:
        return (
            "🔴",
            "Risco elevado detectado (dados sensíveis / PCI / identificadores fortes).",
        )
    if apg_rows or db_rows or filesystem_findings > 0:
        return "🟡", "Risco moderado — priorizar mitigação e validação com negócio/DPO."
    return "🟢", "Nenhum achado catalogado nesta sessão."


def generate_executive_report(
    *,
    session_id: str,
    about: dict[str, str],
    manifest: dict[str, Any],
    db_rows: list[dict],
    fs_rows: list[dict],
    _fail_rows: list[dict],
    apg_rows: list[dict[str, Any]],
    report_rows_capped: bool,
) -> str:
    """
    Produz Markdown executivo: status, achados agregados por sensibilidade (só padrões e
    contagens), Top 3 recomendações APG, postura SRE resumida.

    Não inclui código interno, SQL gerado nem amostras de dados.

    ``_fail_rows`` reserva-se para alinhar a assinatura ao armazenamento da sessão; as contagens
    de falha expostas ao stakeholder vêm do manifest (sem detalhes de erro crus).
    """
    fc = manifest["scope_snapshot"]["findings_counts"]
    emoji, status_label = _executive_status_emoji_and_label(
        db_rows,
        apg_rows,
        int(fc.get("filesystem_findings") or 0),
    )
    tables_n = manifest["scope_snapshot"]["unique_database_tables_with_findings"]
    dur = manifest["scan_window"].get("duration_minutes")
    audit = manifest.get("audit_trail", {})
    bullets = audit.get("dba_facing_summary_pt") or []
    dur_txt = (
        f"{dur} minutos"
        if dur is not None
        else "— (defina `finished_at` na sessão para estimar duração)"
    )

    by_risk = group_findings_by_risk(db_rows, fs_rows)
    labels = {
        "HIGH": "Alta sensibilidade",
        "MEDIUM": "Média sensibilidade",
        "LOW": "Baixa sensibilidade",
    }

    product = about.get("name", "Data Boar")
    version = about.get("version", "")
    sid_show = safe_session_prefix(session_id, max_len=16)
    lines: list[str] = [
        f"# {product} — inteligência e governança de risco (relatório executivo)",
        "",
        "*Enterprise data discovery & risk governance engine — executive desk output.*",
        "",
        f"**Versão:** `{version}` · **Sessão:** `{sid_show}…` · **Emitido (UTC):** `{manifest['engine_signature']['manifest_generated_at_utc']}`",
        "",
        "**Foco:** redução de risco e próximos passos de governança — não substitui parecer jurídico nem runbook de mudança em produção.",
        "",
        "## 1. Status",
        "",
        f"{emoji} **{status_label}**",
        "",
        f"- **Tabelas (BD) com pelo menos um achado:** {tables_n}",
        f"- **Volume agregado:** {fc['database_findings']} achados em base · "
        f"{fc['filesystem_findings']} em arquivos · {fc['scan_failures']} falhas de alvo",
        "",
        "## 2. Resumo executivo (DPO/CISO) — plano de ação",
        "",
        "*Linguagem executiva: cada tipo de dado encontrado é mapeado a um artigo da "
        "LGPD/GDPR e a uma remediação de maior alavancagem. Não substitui parecer "
        "jurídico — o DPO valida o enquadramento por engajamento.*",
        "",
    ]
    dpo_payload = build_dpo_action_plan(apg_rows)
    lines.extend(render_dpo_action_plan_md(dpo_payload))
    lines.extend(
        [
            "## 3. Achados por nível de sensibilidade (apenas padrões e contagens)",
            "",
            "*Não são listados nomes de colunas nem conteúdo amostrado — reduz exposição desnecessária para quem não tem acesso ao detalhe operacional.*",
            "",
        ]
    )

    for key in ("HIGH", "MEDIUM", "LOW"):
        block = by_risk.get(key) or {"total": 0, "pattern_counts": {}}
        total = int(block.get("total") or 0)
        pats: dict[str, int] = block.get("pattern_counts") or {}
        if total == 0:
            lines.append(f"### {labels[key]}")
            lines.append("_Nenhum achado nesta faixa._")
            lines.append("")
            continue
        lines.append(f"### {labels[key]} — **{total}** achado(s)")
        parts = [f"`{name}`: **{cnt}**" for name, cnt in list(pats.items())[:12]]
        lines.append(
            "- " + "; ".join(parts) if parts else "- _(padrão não classificado)_"
        )
        if len(pats) > 12:
            lines.append(
                f"- _… +{len(pats) - 12} padrões adicionais (ver relatório completo interno)._"
            )
        lines.append("")

    st = manifest.get("safety_tags") or {}
    timeout_block = st.get("statement_timeout") or {}
    resolved = timeout_block.get("resolved_sql_hint_ms")
    explicit = timeout_block.get("first_database_target_explicit_ms")
    cap = st.get("sampling_row_cap_resolved")
    lead_comment = st.get("leading_sql_comment") or "-- Data Boar Compliance Scan"

    lines.extend(
        [
            "## 4. Metodologia e segurança",
            "",
            f"- **Duração aproximada do scan:** {dur_txt}",
            (
                "- **Contenção de I/O (sampling):** leituras usam **amostragem** com tetos por coluna "
                "após política de configuração (`SamplingProvider` / `file_scan.sample_limit`) e, "
                "quando definida, a variável de ambiente **`DATA_BOAR_SQL_SAMPLE_LIMIT`** — reduz "
                "pressão de leitura na heap de negócio."
            ),
        ]
    )
    if cap is not None:
        lines.append(f"- **Teto de linhas (valor resolvido):** `{cap}`.")
    if resolved is not None:
        lines.append(
            f"- **Orçamento de timeout por instrução de amostra (hint/env):** `{int(resolved)}` ms."
        )
    if explicit is not None and int(explicit or 0) > 0:
        lines.append(
            f"- **Timeout explícito no primeiro alvo `database` da config:** `{int(explicit)}` ms."
        )
    lines.extend(
        [
            (
                "- **Isolamento transacional e leitura:** o produto **não** promete isolamento "
                "serializável global; aplica **timeouts** e **amostragem** por dialeto. Em "
                "**PostgreSQL**, costuma usar **`SET LOCAL statement_timeout`** em transação curta. "
                "Em **Microsoft SQL Server**, leituras de amostra **podem** incluir **`WITH (NOLOCK)`** "
                "quando esse motor participa da sessão (leitura não bloqueante; sem garantias ACID "
                "estritas) — confira os bullets abaixo e `docs/USAGE.md`. Valide com DBA antes de "
                "aumentar carga em produção."
            ),
            (
                f"- **Rastreabilidade:** instruções de amostra levam o comentário de linha "
                f"`{lead_comment}` onde o dialeto aplica — útil em visões de atividade do motor."
            ),
            "",
            "**Bullets técnicos (evidência do manifesto):**",
            "",
        ]
    )
    for b in bullets[:12]:
        lines.append(f"- {b}")
    if len(bullets) > 12:
        lines.append(f"- *(+{len(bullets) - 12} itens no `scan_manifest_*.yaml`.)*")

    sorted_apg = sort_apg_rows(apg_rows)
    lines.extend(
        [
            "",
            "## 5. Plano de ação (APG) — detalhe técnico",
            "",
            "### 5.1 Prioridades imediatas (Top 3)",
            "",
        ]
    )
    top3 = top_n_recommendations(apg_rows, 3)
    if not top3:
        lines.append(
            "_Sem recomendações agregadas — reexecutar com alvos configurados._"
        )
    else:
        for i, row in enumerate(top3, 1):
            pat = row.get("pattern_detected", "")
            lines.append(
                f"{i}. **`{pat}`** — {row.get('risk_band', '')}: {row.get('recommended_action', '')}"
            )

    lines.extend(
        [
            "",
            "### 5.2 Inventário por tipo de dado (achado → risco → recomendação técnica)",
            "",
        ]
    )
    if not sorted_apg:
        lines.append("_Nenhum tipo agregado para o inventário APG nesta sessão._")
    else:
        for row in sorted_apg:
            pat = str(row.get("pattern_detected") or "(empty)")
            n = int(row.get("finding_count") or 0)
            risk = str(row.get("risk_band", "") or "—")
            action = str(row.get("recommended_action", "") or "—")
            impact = str(row.get("business_impact", "") or "").strip()
            shadow_n = int(row.get("shadow_name_heuristic_count") or 0)
            lines.append(f"#### `{pat}` — **{n}** ocorrência(s)")
            lines.append(f"- **Risco:** {risk}")
            if impact:
                lines.append(f"- **Impacto:** {impact}")
            lines.append(f"- **Recomendação técnica:** {action}")
            if shadow_n > 0:
                lines.append(
                    f"- *Heurística “shadow/staging” no nome do objeto:* **{shadow_n}** achado(s) "
                    "— validar se o ativo ainda é necessário em produção."
                )
            lines.append("")

    lines.extend(
        [
            "",
            "---",
            "",
            f"**Evidência técnica:** `scan_manifest_{sid_show}.yaml`",
            "",
        ]
    )
    if report_rows_capped:
        lines.append(
            "_Nota: licença de avaliação pode limitar linhas no Excel; contagens acima refletem "
            "a sessão completa na base local._"
        )
    return "\n".join(lines) + "\n"


__all__ = ["generate_executive_report"]
