# Aggregated identification tuning (Phase C practical guide)

This runbook helps operators tune aggregated-identification behavior for real scan conditions, especially when coverage is partial or data has high-regret categories.

Related baseline reference: [../SENSITIVITY_DETECTION.md](../SENSITIVITY_DETECTION.md#aggregated-identification-configuration-and-examples)

---

## Quick objective

Choose a configuration profile that balances:

- **Recall** (catching possible re-identification situations)
- **Noise** (amount of suggested-review rows to triage)
- **Coverage reality** (full dataset vs sampled/incremental windows)

---

## Practical profiles

### Profile A: Conservative baseline (default)

Use when scans are broad and review capacity is limited.

```yaml
detection:
  aggregated_identification_enabled: true
  aggregated_min_categories: 2
  aggregated_incomplete_data_mode: false
  aggregated_single_high_risk_suggested_review: false
```

Expected behavior:

- Stable and conservative output.
- Fewer MEDIUM suggested-review rows.

### Profile B: Partial coverage scans

Use for sampled datasets, narrow date windows, or staged connector rollout.

```yaml
detection:
  aggregated_identification_enabled: true
  aggregated_min_categories: 2
  aggregated_incomplete_data_mode: true
  aggregated_single_high_risk_suggested_review: false
```

Expected behavior:

- Effective category threshold is lowered by 1 (minimum 1).
- Better recall under incomplete evidence, with moderate noise increase.

### Profile C: High-regret health context

Use when missing potential health-linked re-identification signals is costlier than extra review.

```yaml
detection:
  aggregated_identification_enabled: true
  aggregated_min_categories: 2
  aggregated_incomplete_data_mode: true
  aggregated_single_high_risk_suggested_review: true
```

Expected behavior:

- Single `health` category can still surface as MEDIUM suggested review.
- Highest recall, highest triage demand.

---

## Operator workflow (recommended)

1. Run one baseline scan with Profile A.
2. If coverage is partial, rerun with Profile B.
3. If domain risk is high (health-heavy), evaluate Profile C.
4. Compare report deltas:
   - count of Cross-ref rows
   - count of MEDIUM suggested-review rows
   - analyst time to review
5. Keep the lowest-noise profile that still captures expected risk cases.

---

## Suggested rollout policy

- Start with Profile A in production-like environments.
- Enable Profile B per target where data completeness is known to be partial.
- Enable Profile C only for explicit high-regret targets and document the reason in the scan notes/change log.

---

## Troubleshooting tips

- Too much noise: disable `aggregated_single_high_risk_suggested_review` first, then reassess.
- Too few findings with sampled data: enable `aggregated_incomplete_data_mode`.
- Unexpected category mapping: review `detection.quasi_identifier_mapping` custom rules for overrides.
