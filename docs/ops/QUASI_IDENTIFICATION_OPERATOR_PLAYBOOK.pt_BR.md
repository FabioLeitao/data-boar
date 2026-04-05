# Playbook do operador: quasi-identificação (token-aware)

**English:** [QUASI_IDENTIFICATION_OPERATOR_PLAYBOOK.md](QUASI_IDENTIFICATION_OPERATOR_PLAYBOOK.md)

Atalho operacional para a frente de quasi-identificação (`IP + geo + breadcrumbs`) com baixa carga cognitiva.

## Objetivo

- Manter o trabalho diário pequeno, seguro e auditável.
- Evitar aumento silencioso de escopo nos sprints de detecção.
- Preservar defaults seguros de LGPD com progresso mensurável.

## Checklist de fatia diária (10-120 min)

Use exatamente uma fatia primária:

1. `score` - ajustar/testar somente score de risco/confiança.
2. `report` - ajustar campos de saída ou mapeamento da matriz.
3. `guardrail` - redação, limites de lookup, proteções de opt-in.
4. `fixture` - adicionar caso sintético para cobrir FN/incerteza.
5. `docs` - atualizar plano/playbook/referências de schema.

## Gates de segurança obrigatórios por fatia

- Enriquecimento online desligado por padrão.
- Sem persistência de payload enriquecido por padrão.
- Redação ligada para evidências no relatório.
- Se houver mudança de comportamento, incluir/atualizar ao menos um teste.

## Referência rápida de ação

| Risco x Confiança | Ação |
| --- | --- |
| LOW x qualquer | Apenas informativo/monitoramento |
| MEDIUM x LOW | Revisão sugerida com nota de incerteza |
| MEDIUM x MEDIUM/HIGH | Fila de revisão prioritária |
| HIGH x LOW | Alerta de alto risco + coletar evidência segura |
| HIGH x MEDIUM/HIGH | Revisão obrigatória do operador |

## Artefatos de contrato

- Schema: `docs/ops/schemas/quasi-identification-risk-record.schema.json`
- Exemplo: `docs/ops/schemas/quasi-identification-risk-record.example.json`
- Plano: `docs/plans/PLAN_QUASI_IDENTIFICATION_COMPOSITE_RISK.md`

## Guia de split de commits (cadência local)

Prefira commits pequenos por tema:

- `docs(plans):` só atualização de plano/sequenciamento.
- `test(detector):` só testes de contrato/fixtures.
- `chore(workflow):` só wrappers/playbook/guia operacional.

Evite misturar código + docs amplas + workflow no mesmo commit, exceto quando o change for realmente atômico.
