# ADR 0044: Opt-in algorithmic checksum gate for CPF and credit-card shapes

## Context

`SensitivityDetector` returns **HIGH** as soon as a built-in regex matches a
shape we recognise (`LGPD_CPF`, `CREDIT_CARD`, `EMAIL`, …). The shape-only
contract is intentionally **FN-first** — it is better to surface a borderline
column than to silently drop it — but two regex families produce a steady
stream of avoidable **false positives** when scanning operational stores:

- **`LGPD_CPF`** matches any 11-digit run with the optional `xxx.xxx.xxx-xx`
  punctuation. Random opaque IDs (`12345678901`), reservation codes, and
  legacy keys all fit the shape without ever being valid CPFs.
- **`CREDIT_CARD`** matches any 16-digit run separated by spaces or hyphens.
  Barcodes, accession numbers, and synthetic test data routinely qualify.

The repository already ships **algorithmic verifiers** for both shapes:

- `core.brazilian_cpf.cpf_checksum_valid` (Receita Federal modulo-11).
- The Pro+ Rust filter (`rust/boar_fast_filter`) and `pro/worker_logic`
  open-core fallback both apply the **Luhn** modulo-10 check before flagging a
  card as a candidate.

Until now the detector did **not** consume those verifiers — `core/detector.py`
flagged shape matches as HIGH on regex alone. That left a documented gap:
the SENSITIVITY_DETECTION guide explicitly noted *“checksum validation … is
left to a future detector phase.”*

The mission triggering this ADR (*sensor tuning & heuristic evolution*) asked
for **Luhn-style** validation on financial PII and **contextual** elevation
for high-confidence numeric shapes, with **zero impact on database locks**
(this work touches only in-process detection, not connector sampling).

## Decision

1. Add a shared **`core.luhn`** module exposing `luhn_check_digits`,
   `luhn_check`, and `string_contains_luhn_valid_card`. The Pro+ worker pool
   (`pro/worker_logic.py`) imports the same helper instead of carrying its
   own copy.
1. Add an **opt-in** detector flag
   `sensitivity_detection.checksum_validation` (default **false**). When
   enabled, regex matches for `LGPD_CPF` and `CREDIT_CARD` are post-filtered
   with the modulo-11 / Luhn helpers **before** they reach the HIGH branch in
   `SensitivityDetector.analyze`.
1. When the gate rejects every shape match for a column and no other strong
   PII regex remains, surface a **MEDIUM** finding with
   `pattern_detected = "CHECKSUM_REJECTED:LGPD_CPF"` (or `:CREDIT_CARD`) and
   `norm_tag = "Shape match without valid check digit"`. The diagnostic is
   intentionally explicit so reviewers can see *why* the demotion happened —
   the **art of the fallback** doctrine forbids silent demotion.
1. The gate **does not** alter `EMAIL`, `LGPD_CNPJ*`, `PHONE_BR`, `CCPA_SSN`,
   or any other regex; those families have no algorithmic check digit defined
   in this repo. Email and other patterns continue to drive HIGH on shape.
1. The flag is **off by default** so existing scans, reports, and Excel
   evidence retain their current FN-first posture.

## Consequences

### Positive

- **Lower false-positive surface** on numeric IDs and barcodes that share the
  CPF / 16-digit-card shape — exactly the columns operators flagged as noisy
  during lab scans.
- **Truthful diagnostic** when a shape match is demoted: `CHECKSUM_REJECTED`
  in the report tells reviewers “the detector saw the shape, the check digit
  said no.” That is auditable evidence; silent reclassification would not be.
- **Single source of Luhn truth.** The Pro+ worker no longer carries its own
  modulo-10 implementation; `core.luhn.luhn_check_digits` is the shared
  reference for Open Core, Pro+ Python, and Rust (the Rust path keeps its
  own implementation but matches the same contract).
- **No connector / database impact.** The change is in-process detection
  only — no new SQL, no new locks, no changes to sampling caps. The
  defensive-scanning manifesto contract with customer databases is untouched.

### Trade-offs

- The gate uses **only** the algorithms that ship in the repository today
  (CPF modulo-11, Luhn modulo-10). It does **not** validate CNPJ check digits
  or BIN ranges; those remain future work.
- **Defaulting off** keeps backward compatibility but means operators must
  flip `sensitivity_detection.checksum_validation: true` (or `--config` /
  CLI passthrough) to get the FP reduction. Documentation calls this out so
  operators do not assume CPF / card columns are auto-validated.
- A row whose only HIGH evidence was a shape-only CPF / 16-digit run will
  drop one band (HIGH → MEDIUM). Existing reports comparing against a
  baseline scan should expect that delta in the first run after enabling.

## References

- [`core/luhn.py`](../../core/luhn.py)
- [`core/brazilian_cpf.py`](../../core/brazilian_cpf.py)
- [`core/detector.py`](../../core/detector.py) (`_any_match_passes_checksum`,
  `SensitivityDetector` constructor flag)
- [`pro/worker_logic.py`](../../pro/worker_logic.py)
- [`tests/test_luhn.py`](../../tests/test_luhn.py)
- [`tests/test_detector_checksum_validation.py`](../../tests/test_detector_checksum_validation.py)
- [`docs/SENSITIVITY_DETECTION.md`](../SENSITIVITY_DETECTION.md) — *Config keys*
  table (`sensitivity_detection.checksum_validation` row)
- [`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
- [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md)
