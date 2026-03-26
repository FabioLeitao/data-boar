# Plan: Bandit (Python security linter)

**Status:** Phase 1–2 done (dev dependency, `pyproject` config, optional CI gate **medium+**). **Phase 3** = tighten skips / per-line `# nosec`, expand paths, or fail on **low** when triaged.

**Synced with:** [PLANS_TODO.md](PLANS_TODO.md)

## Purpose

**Bandit** finds common security anti-patterns (assert in “production”, `try/except/pass`, subprocess usage, weak crypto hints, naive SQL string detection) that **unit tests may not cover**. It **complements** **CodeQL**, **Semgrep**, and **Ruff**—different engines, different rules.

**Config:** `[tool.bandit]` in **`pyproject.toml`** (`exclude_dirs`, `skips`). **CI:** `.github/workflows/ci.yml` job **Bandit** runs **`bandit -c pyproject.toml -r … -ll`** (report **medium** and **high** only so known **low**-severity noise does not block merges while triage proceeds).

---

## Phases

| Phase | Content                                                                                                                                                                                                                                    | Status    |
| ----- | -------                                                                                                                                                                                                                                    | ------    |
| **1** | Add **`bandit`** to **`[dependency-groups] dev`** (`uv add --dev bandit`); document local command.                                                                                                                                         | ✅ Done    |
| **2** | Add **`[tool.bandit]`** in **`pyproject.toml`**: `exclude_dirs`, initial **`skips`** (e.g. **B608** for vetted identifier-built SQL — same story as [PLAN_SEMGREP_CI.md](PLAN_SEMGREP_CI.md) Semgrep exclude). CI job **medium+** (`-ll`). | ✅ Done    |
| **3** | Triage **low** findings (`-i` or full report): fix, **`# nosec Bxxx`** with one-line justification, or extend **`skips`** / per-file config after review. Optionally raise CI to **low** once clean.                                       | ⬜ Pending |
| **4** | Update **`.cursor/skills/quality-sonarqube-codeql/SKILL.md`** and **`.cursor/rules/quality-sonarqube-codeql.mdc`** when running Bandit after security-sensitive edits (habit, not always full suite).                                      | 🔄 Ongoing |

---

## Commands

```bash
# Medium + high only (matches CI)
uv run bandit -c pyproject.toml -r api core config connectors database file_scan report main.py -ll -q

# Full triage (includes low)
uv run bandit -c pyproject.toml -r api core config connectors database file_scan report main.py -i
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

## Last updated

2026-03-25 — Dev dependency, `pyproject` `[tool.bandit]`, CI job, plan doc.
