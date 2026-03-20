# Ajuste de identificação agregada (guia prático da Fase C)

Este runbook ajuda operadores a ajustar o comportamento de identificação agregada em condições reais de scan, especialmente quando a cobertura é parcial ou quando há categorias de alto arrependimento.

Referência de base: [../SENSITIVITY_DETECTION.pt_BR.md](../SENSITIVITY_DETECTION.pt_BR.md#identificação-agregada-configuração-e-exemplos)

---

## Objetivo rápido

Escolher um perfil de configuração que equilibre:

- **Recall** (capturar possíveis situações de reidentificação)
- **Ruído** (quantidade de linhas de revisão sugerida para triagem)
- **Realidade da cobertura** (dataset completo vs janelas amostradas/incrementais)

---

## Perfis práticos

### Perfil A: Linha de base conservadora (padrão)

Use quando os scans são amplos e a capacidade de revisão é limitada.

```yaml
detection:
  aggregated_identification_enabled: true
  aggregated_min_categories: 2
  aggregated_incomplete_data_mode: false
  aggregated_single_high_risk_suggested_review: false
```

Comportamento esperado:

- Saída estável e conservadora.
- Menos linhas MEDIUM de revisão sugerida.

### Perfil B: Scans com cobertura parcial

Use para datasets amostrados, janelas curtas de data ou rollout por etapas de conectores.

```yaml
detection:
  aggregated_identification_enabled: true
  aggregated_min_categories: 2
  aggregated_incomplete_data_mode: true
  aggregated_single_high_risk_suggested_review: false
```

Comportamento esperado:

- O limiar efetivo de categorias cai em 1 (mínimo 1).
- Melhor recall com evidência incompleta, com aumento moderado de ruído.

### Perfil C: Contexto de saúde com alto arrependimento

Use quando perder sinais potenciais de reidentificação ligados a saúde é mais custoso do que revisar casos extras.

```yaml
detection:
  aggregated_identification_enabled: true
  aggregated_min_categories: 2
  aggregated_incomplete_data_mode: true
  aggregated_single_high_risk_suggested_review: true
```

Comportamento esperado:

- Categoria única `health` ainda pode aparecer como MEDIUM de revisão sugerida.
- Maior recall, maior carga de triagem.

---

## Fluxo operacional (recomendado)

1. Rode um scan base com o Perfil A.
2. Se a cobertura for parcial, rode novamente com o Perfil B.
3. Se o risco de domínio for alto (forte presença de saúde), avalie o Perfil C.
4. Compare os deltas no relatório:
   - total de linhas Cross-ref
   - total de linhas MEDIUM de revisão sugerida
   - tempo de análise humana
5. Mantenha o perfil com menor ruído que ainda capture os riscos esperados.

---

## Política de rollout sugerida

- Comece com Perfil A em ambientes tipo produção.
- Ative Perfil B por alvo quando a cobertura de dados for sabidamente parcial.
- Ative Perfil C apenas para alvos de alto arrependimento e registre o motivo nas notas do scan/log de mudança.

---

## Dicas de troubleshooting

- Ruído alto: desative primeiro `aggregated_single_high_risk_suggested_review` e reavalie.
- Poucos achados com dados amostrados: ative `aggregated_incomplete_data_mode`.
- Mapeamento de categoria inesperado: revise regras customizadas em `detection.quasi_identifier_mapping`.
