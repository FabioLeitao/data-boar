# Plan: Detection and differential treatment of possible minor data

## Goal

Detect when gathered personal data may relate to **minors** (e.g. inferred from date of birth in samples) and treat it as **highest sensitivity**. Cross-reference with name, official documents (CPF, RG, etc.), and health information when available. When there is an indication of data from a minor, optionally perform a **full scan** of the relevant columns and adjacent information to confirm the condition and apply **differential treatment** in the report (LGPD Art. 14, GDPR Art. 8, consent of holder, etc.), surfacing it as more important than other findings.

## Principles (non-destructive, no regression)

- **Additive only:** New logic is optional (config or automatic but backward-compatible). Existing sensitivity levels (HIGH/MEDIUM/LOW) and report layout remain valid.
- **No performance regression:** Full-scan of columns for minor confirmation is optional and scoped (e.g. only when DOB suggests minor).
- **No weakening of security:** No storage of raw sample content; only metadata (e.g. possible_minor flag, norm_tag extension).
- **Tests:** New code paths covered by tests; existing tests must still pass.

---

## Approach (high level)

1. **Age from DOB**  
   In the detector (or a dedicated post-step), parse **date-of-birth** patterns from column names and sample text (reuse DATE_DMY and similar; add DOB-specific patterns if needed). Compute **age** as (reference date − DOB). If age &lt; 18 (or configurable threshold), treat as **possible minor**.

2. **Highest sensitivity**  
   Either:
   - Introduce a new level **CRITICAL** (or **MINOR**) ordered above HIGH in filters and reporting, or  
   - Keep HIGH and add an optional **flag** (e.g. `possible_minor` / `minor_data_indicator`) on findings so reports can show “possible minor data” with highest priority.  
   Recommendation: **flag** to avoid changing the existing three-level contract everywhere; report and filters treat “HIGH + possible_minor” as highest.

3. **Cross-reference**  
   When a finding is DOB/age suggesting minor, **cross-reference** with:
   - Same row/record: name-like columns, official doc (CPF, RG, SSN), health-related columns.  
   If the same logical record has DOB (minor) + name/doc/health, treat as **confirmed or high-confidence** “possible minor data” and ensure it is clearly prioritized in the report.

4. **Full scan when possible minor**  
   When DOB/age suggests a minor, optionally:
   - **Full scan** of that column (all values, not only sample) to confirm presence of dates indicating minors.  
   - **Scan adjacent columns** (same table: name, doc, health) to support cross-reference.  
   This may require connector/engine support (e.g. “rescan column with full content”, “scan related columns”). Implement as **optional** (config-driven) to avoid performance impact.

5. **Report**  
   - Add a **recommendation** (or dedicated section/sheet) for **“Possible data of minors”** with **highest priority** (above CRÍTICA where applicable) and **differential treatment** text (LGPD Art. 14, GDPR Art. 8, consent, parental responsibility, etc.).  
   - In Report info or Recommendations, **surface possible-minor findings** so they are clearly more prominent than other gathered data that triggered notifications.

6. **Config**  
   Optional settings, e.g.:
   - `detection.minor_age_threshold` (default 18).  
   - `detection.minor_full_scan` (default false): when true, full-scan column and adjacent when DOB suggests minor.  
   - `detection.minor_cross_reference` (default true): use name/doc/health in same row to boost confidence.

---

## Sequential to-dos

Execute in order; each step should be tested and non-regressing before the next.

| # | To-do | Status |
|---|--------|--------|
| 1 | **Design & doc:** Finalize approach (age inference, flag vs new level, cross-ref, full-scan scope) and document in this file; ensure schema/API impact is minimal (optional column or flag). | ⬜ Pending |
| 2 | **Detector – DOB/age:** Add date parsing (DOB) and age calculation (stdlib); when age &lt; threshold, set internal flag or level for “possible minor”. Do not change existing HIGH/MEDIUM/LOW for non-minor findings. | ⬜ Pending |
| 3 | **Schema (optional):** Add optional column `possible_minor` (or `minor_data_indicator`) to database_findings and filesystem_findings with migration; or encode via norm_tag/pattern_detected (e.g. pattern “DOB_POSSIBLE_MINOR”). | ⬜ Pending |
| 4 | **Scanner/connector:** Pass “possible minor” from detector into saved findings (store flag or special pattern/norm_tag). | ⬜ Pending |
| 5 | **Cross-reference:** When a finding is DOB/possible_minor, correlate with other columns in same table/row (name, CPF/RG/SSN, health-related). Optionally set “confirmed” or “high_confidence” minor indicator. May require scanner to supply row context or a post-processing step. | ⬜ Pending |
| 6 | **Full scan (optional):** When DOB suggests minor and config enables it, trigger full scan of that column and related columns (engine/connector). Document as optional; default off. | ⬜ Pending |
| 7 | **Report:** Add recommendation row or section for “Possible data of minors” with highest priority and differential treatment (LGPD Art. 14, GDPR Art. 8, consent, etc.). Ensure possible-minor findings are listed and clearly prioritized above other findings. | ⬜ Pending |
| 8 | **Config:** Add optional `detection.minor_age_threshold`, `detection.minor_full_scan`, `detection.minor_cross_reference` in config loader (defaults: 18, false, true). | ⬜ Pending |
| 9 | **Tests:** Unit tests for age inference, for possible_minor flag, for report prioritization; full test suite passes with no regression. | ⬜ Pending |
| 10 | **Docs:** Update sensitivity-detection and compliance docs (EN and PT-BR) to describe possible-minor detection and differential treatment. | ⬜ Pending |

---

## References

- LGPD Art. 14 (children’s data).  
- GDPR Art. 8 (child’s consent in relation to information society services).  
- Existing detector: `core/detector.py` (regex + ML + DL; returns sensitivity_level, pattern_detected, norm_tag).  
- Existing report: `report/generator.py` (`_recommendations_rows`, Report info, findings sheets).  
- DB schema: `core/database.py` (DatabaseFinding, FilesystemFinding; sensitivity_level String(20)).

---

*This plan is additive and aims to avoid breaking existing behaviour, performance, or sensitivity for non-minor data.*
