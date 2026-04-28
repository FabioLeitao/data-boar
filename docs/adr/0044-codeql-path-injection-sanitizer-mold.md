# ADR 0044: CodeQL `py/path-injection` sanitizer mold (basename allowlist + normpath/startswith/isfile)

## Context

PR [#283](https://github.com/FabioLeitao/data-boar/pull/283) hardened heatmap path handling in [`report/generator.py`](../../report/generator.py) by:

- resolving both `output_dir` and `heatmap_path` with `Path.resolve()`,
- requiring `candidate.is_relative_to(base)` (instead of `Path.relative_to` + `ValueError`),
- and routing `session_id` through `safe_session_prefix()` for output filenames.

CI ran clean on **Bandit (medium+)**, **Dependency audit**, **Lint (pre-commit)**, **Semgrep**, **SonarQube/SonarCloud**, **Test (Python 3.12 / 3.13)**, and the duplicate **CodeQL** "Analyze (Python)" job from `.github/workflows/codeql.yml`. The **GitHub Advanced Security** CodeQL check still failed with one `high` annotation:

> `report/generator.py:46` — *Uncontrolled data used in path expression* — "This path depends on a user-provided value."

The same project already ships an **accepted** sanitizer mold for the dashboard report and heatmap download endpoints in [`api/routes.py`](../../api/routes.py): `_real_file_under_out_dir_str` reduces the input to a **single basename**, validates it against an `re.fullmatch` allowlist, then runs `normpath(join(base, name))` + `startswith(base)` + `isfile()` against a `realpath`-canonical base. CodeQL recognises that pattern; it does **not** recognise `Path.resolve()` + `Path.is_relative_to()` as a barrier in `py/path-injection` data-flow.

The other production rules that frame this decision:

- [`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) — "no surprise side effects" extends to the report writer: filenames must never let an attacker pivot away from the operator-controlled output directory.
- [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../ops/inspirations/THE_ART_OF_THE_FALLBACK.md) — when the strongest containment check fails, **degrade silently to "no embed"** rather than continuing with an unverified path; emit nothing instead of a leaked sink.

## Decision

1. **Sanitizer mold for `report/generator.py`** is the same as `api/routes.py`:
   - **Whitelist barrier** `_heatmap_basename(path)` — `os.path.basename` then `re.fullmatch(_HEATMAP_BASENAME_PATTERN, name)` (allowlist `^heatmap_[A-Za-z0-9_-]{4,64}\.png$`). CodeQL treats `re.fullmatch` against a literal regex as a path-traversal sanitizer.
   - **Containment** `_safe_heatmap_path_under_output_dir(path, output_dir)` — `os.path.realpath(os.path.abspath(os.fspath(output_dir)))` for the canonical base, then `os.path.normpath(os.path.join(base, name))` + `fullpath.startswith(base)` + `os.path.isfile(fullpath)`. The **basename** is the only segment that flows into the join; the original `path` argument is never re-used as a join input.
2. **No `Path.is_relative_to` reliance** in `report/generator.py` for sinks that load a file (`OpenpyxlImage(str(path))`, `plt.savefig`, etc.). `Path.is_relative_to` may be useful for application logic, but it is **not** treated as a sanitizer by CodeQL `py/path-injection`.
3. **Filename construction** that incorporates `session_id` always goes through `report.safe_prefix.safe_session_prefix(...)` (regex-restricted to `[A-Za-z0-9_-]`, capped length, falls back to the literal `session`). This stops `session_id` from injecting `..` or path separators into report or heatmap output names — same posture as ADR 0034 on outbound discovery identity (controlled inputs only).
4. **Behaviour on rejection** is silent fallback: when the heatmap basename is off-allowlist or fails containment, the generator simply does not embed the image and the Excel still ships. This honours the `THE_ART_OF_THE_FALLBACK.md` "diagnostic on fall" rule — the failure mode is observable (`pass` branch in the embed try/except) without raising and without writing a sink.

## Consequences

- **Positive:** CodeQL `py/path-injection` recognises the sanitizer Colleague-Nn and stops flagging the heatmap embed sink. The same mold is now reused across `api/routes.py` and `report/generator.py`, so a future contributor extending the report writer can copy the helper signature instead of reinventing one. Regression guard lives in [`tests/test_report_generator_path_safety.py`](../../tests/test_report_generator_path_safety.py); the previous helper name `_heatmap_path_under_output_dir` is kept as a module-level alias for backwards compatibility (any external import path stays valid).
- **Trade-off:** Strictly basename-based containment means a caller cannot point the embed at a heatmap that lives in a sibling directory; today the generator only ever produces heatmaps under `output_dir`, so this is the desired posture. If a future feature needs cross-directory heatmaps, it must extend the allowlist explicitly (and add tests), not reach back to `Path.is_relative_to`.
- **Database / blast radius:** Zero. The fix touches only filename validation and image embedding in `report/generator.py`; no SQL, connector, or DB-state code is modified. The `DEFENSIVE_SCANNING_MANIFESTO.md` clauses on read-only sampling, isolation, and statement attribution are unaffected.

## References

- [`report/generator.py`](../../report/generator.py) — `_heatmap_basename`, `_safe_heatmap_path_under_output_dir`, `_HEATMAP_BASENAME_PATTERN`.
- [`api/routes.py`](../../api/routes.py) — `_real_file_under_out_dir_str`, `_resolved_existing_file_under_out_dir`, `_HEATMAP_FILENAME_PATTERN` (CodeQL-accepted sibling).
- [`report/safe_prefix.py`](../../report/safe_prefix.py) — `safe_session_prefix` for session-id-derived filenames.
- [`tests/test_report_generator_path_safety.py`](../../tests/test_report_generator_path_safety.py), [`tests/test_report_path_safety.py`](../../tests/test_report_path_safety.py), [`tests/test_safe_prefix.py`](../../tests/test_safe_prefix.py) — regression coverage.
- CodeQL: [`py/path-injection`](https://codeql.github.com/codeql-query-help/python/py-path-injection/) (sanitizer guidance: basename + `normpath`/`startswith` containment).
- PR [#283](https://github.com/FabioLeitao/data-boar/pull/283) — original RCA in the Slack thread that triggered this ADR.
