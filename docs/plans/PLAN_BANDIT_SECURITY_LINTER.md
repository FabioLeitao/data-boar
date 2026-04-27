# Plan: Bandit (Python security linter)

**Status:** Phase 1–3 done (dev dependency, `pyproject` config, CI gate **low+**, every previously-flagged low finding triaged with per-line `# nosec BXXX` + a one-line comment anchored to **`docs/ops/inspirations/`** doctrine). **Phase 4** = ongoing habit (run after security-sensitive edits; revisit `[tool.bandit] skips` annually).

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md)

## Purpose

**Bandit** finds common security anti-patterns (assert in “production”, `try/except/pass`, subprocess usage, weak crypto hints, naive SQL string detection) that **unit tests may not cover**. It **complements** **CodeQL**, **Semgrep**, and **Ruff**—different engines, different rules.

**Config:** `[tool.bandit]` in **`pyproject.toml`** (`exclude_dirs`, `skips`). **CI:** `.github/workflows/ci.yml` job **Bandit** runs **`bandit -c pyproject.toml -r … -l`** (report **low**, **medium**, and **high**; the triage in Phase 3 means a re-introduced low finding is now a real signal, not noise). **Regression guard:** **`tests/test_bandit_low_clean.py`** runs the same CLI string locally so contributors trip before CI does.

---

## Phases

| Phase | Content                                                                                                                                                                                                                                    | Status    |
| ----- | -------                                                                                                                                                                                                                                    | ------    |
| **1** | Add **`bandit`** to **`[dependency-groups] dev`** (`uv add --dev bandit`); document local command.                                                                                                                                         | ✅ Done    |
| **2** | Add **`[tool.bandit]`** in **`pyproject.toml`**: `exclude_dirs`, initial **`skips`** (e.g. **B608** for vetted identifier-built SQL — same story as [PLAN_SEMGREP_CI.md](completed/PLAN_SEMGREP_CI.md) Semgrep exclude). CI job **medium+** (`-ll`). | ✅ Done    |
| **3** | Triage all 41 **low** findings: per-line **`# nosec BXXX`** with a one-line "why" comment above (anchored to **`DEFENSIVE_SCANNING_MANIFESTO.md`** clause 1 and **`THE_ART_OF_THE_FALLBACK.md`** §3 "diagnostic on fall"). Bump CI gate to **`-l`** (low+); add **`tests/test_bandit_low_clean.py`** as the local regression guard. | ✅ Done    |
| **4** | Update **`.cursor/skills/quality-sonarqube-codeql/SKILL.md`** and **`.cursor/rules/quality-sonarqube-codeql.mdc`** when running Bandit after security-sensitive edits (habit, not always full suite).                                      | 🔄 Ongoing |

---

## Commands

```bash
# Same gate as CI (low + medium + high; Phase 3 triage means zero findings is the contract)
uv run bandit -c pyproject.toml -r api core config connectors database file_scan report main.py -l -q

# Full triage with confidence column (-i adds confidence, -v prints metrics per file)
uv run bandit -c pyproject.toml -r api core config connectors database file_scan report main.py -i

# Regression guard (same CLI, asserted from pytest)
uv run pytest tests/test_bandit_low_clean.py -v
```

**Scope:** Aligns with Ruff `extend-exclude` legacy dirs; **`tests/`** excluded from Bandit paths by default (add only if you want to lint test code for `assert` / mocks).

---

## Relationship to Semgrep / CodeQL

| Tool        | Role                                                                                               |
| ----        | ----                                                                                               |
| **CodeQL**  | Deep semantic queries; GitHub Security tab.                                                        |
| **Semgrep** | Registry rules + fast PR signal (`p/python`).                                                      |
| **Bandit**  | AST plugin style; good for **assert**, **subprocess**, **try/except/pass**, heuristic SQL strings. |

---

## Triage rules (Phase 3 — keep this in mind for new code)

- **B110 / B112 (`try/except/pass`, `try/except/continue`):** allowed only when the swallowed
  exception is **best-effort telemetry, optional cleanup, or per-row sampling fallback** that
  must never abort the customer scan. Annotate with **`# nosec B110`** (or `B112`) on the
  `pass`/`continue` line and a one-line comment immediately above explaining *why*, anchored
  to **`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`** (clause 1: "no surprise side
  effects") or **`THE_ART_OF_THE_FALLBACK.md`** (§3 diagnostic-on-fall).
- **B603 / B607 (subprocess on PATH):** allowed only with a **fixed argv list** (no shell, no
  user-controlled binary path) and a **graceful degraded path** when the binary is missing
  (e.g. `ffprobe` → return `""`). Document the rationale at the call site, **not** at import
  time alone — a future refactor that reuses the import must re-justify.
- **B105 (hardcoded password string):** allowed for **public endpoint URL templates** that
  Bandit's heuristic flags as credential-shaped (e.g. Azure AD token URL). Annotate inline.
- **B101 (assert in production):** allowed only as a **type-narrowing assertion after** an
  explicit `if x is None: raise RuntimeError(...)` block, so callers under `python -O` still
  fail loudly instead of dereferencing `None`.

If a finding does not fit one of the categories above, **fix the code** instead of adding
`# nosec`. The regression guard exists so the next contributor cannot quietly invert that
order.

## Last updated

2026-04-27 — Phase 3 done: 41/41 low findings triaged with per-line nosec + doctrine-anchored
comments, CI gate raised to `-l`, regression guard added.
