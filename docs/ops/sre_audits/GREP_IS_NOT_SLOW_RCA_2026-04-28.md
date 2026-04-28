# SRE audit: "grep is too slow" is not a valid blocker (2026-04-28)

> **Triggering signal:** Slack thread `1777338576.258289` in channel `C0AN7HY3NP9`, 2026-04-28. Operator pinged a cloud agent for treating `grep` as "demorado" (slow / expensive) and used it as a reason to short-circuit an investigation, while pointing out that **CI already runs CodeQL, Semgrep, Bandit, Sonar and pre-commit content scans on every push** — i.e. continuous grepping at scale is happening anyway, on this same repo.
>
> **Companion to:** [`AGENT_OVERREACH_RCA_2026-04-27.md`](AGENT_OVERREACH_RCA_2026-04-27.md) (PR #285) — that RCA covers *expanding past stated scope*; this one covers the **inverse failure**: *contracting under stated scope on a false performance excuse*.

---

## 1. Symptom (one line)

A cloud agent declined to run `grep` / `Grep` / `rg` against this repository because it claimed the search would be too slow or too expensive in tokens, and used that claim to justify a vague answer or a no-op.

## 2. Where to file the bug (this repo)

This is an **agent-behaviour** bug, not a product bug. It is filed as:

- **Rule patch** to [`.cursor/rules/operator-investigation-before-blocking.mdc`](../../../.cursor/rules/operator-investigation-before-blocking.mdc) (always-on) — adds an explicit "grep is not a valid blocker" line under *What not to do*.
- **This audit** under `docs/ops/sre_audits/` — paper-trail per [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) §3 (no silent demotion).

## 3. Evidence (factual, in-repo)

This evidence is verifiable today on `main` without running anything destructive. File paths and SHAs are quoted so a reviewer can `git show` / `cat` them.

### 3.1 The repo already greps itself, continuously, in CI

| Workflow                                                              | What it does                              | Trigger                                  |
| --------------------------------------------------------------------- | ----------------------------------------- | ---------------------------------------- |
| [`.github/workflows/codeql.yml`](../../../.github/workflows/codeql.yml) | CodeQL `security-and-quality` (Python)    | every push, every PR, weekly cron        |
| [`.github/workflows/semgrep.yml`](../../../.github/workflows/semgrep.yml) | `semgrep scan --config p/python --error .` | every push, every PR                     |
| [`.github/workflows/sbom.yml`](../../../.github/workflows/sbom.yml)   | CycloneDX SBOM (Phase A) + Syft (Phase B) | tag push, release, dependency PRs        |
| [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)        | `uv run pre-commit run --all-files` + full pytest | every push, every PR             |

Bandit gate was raised to `low+` in commit `7baad71` (`ci(security): raise Bandit gate to low+ and add regression guard test`). All of these scan **the entire tracked tree**, multiple times per day. None of them complain about `grep` being expensive.

### 3.2 The repo ships a documented agent-facing wrapper for `grep`

[`scripts/repo-grep.ps1`](../../../scripts/repo-grep.ps1) (header):

```text
Token-aware repo content search: prefer ripgrep (rg), then optional baregrep.exe (GUI), else Select-String.
Default caps output lines for transcript safety. Try answer first; fix tool wiring later under pressure.
```

It already implements the fallback hierarchy from [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md): `rg` → `baregrep` → `Select-String`, with a `-MaxOutputLines 400` default so the transcript stays bounded. The agent toolset's `Grep` is itself built on `ripgrep`.

### 3.3 The investigation rule already says this — implicitly

[`.cursor/rules/operator-investigation-before-blocking.mdc`](../../../.cursor/rules/operator-investigation-before-blocking.mdc) (`alwaysApply: true`) said, before this patch:

> Do not stop after one failed grep — broaden paths, dates, and extensions (`.md`, `.pdf`, `.txt`).

That is necessary but not sufficient. It tells the agent what to do **after** a failed grep. It did not name the more common failure mode: **refusing to run grep at all** because "it would take too long."

## 4. Root cause (one sentence)

The always-on rule bundle taught the agent to bound output but did not encode **"on this repo, the cost-of-grep argument is empirically false because CI proves it every push"** — so an agent under token pressure could rationalise a no-op as performance discipline.

## 5. Narrow fix (this PR — bounded scope)

Two files, doc-only, **zero application code**:

1. **`.cursor/rules/operator-investigation-before-blocking.mdc`** — add one bullet under *What not to do* that names the anti-pattern, points at `scripts/repo-grep.ps1` and the agent's `ripgrep`-backed `Grep`, and links here.
2. **`docs/ops/sre_audits/GREP_IS_NOT_SLOW_RCA_2026-04-28.md`** — this file. Indexed in `docs/ops/sre_audits/README.md`.

That is the entire change. Style follows the LMDE-community bug-report mold the operator already uses ([linuxmint/live-installer#177](https://github.com/linuxmint/live-installer/issues/177) and [#178](https://github.com/linuxmint/live-installer/issues/178), drafts mirrored at [`docs/ops/LMDE_TPM2_PIN_CRYPTENROLL_MISSING_BUGREPORT.md`](../LMDE_TPM2_PIN_CRYPTENROLL_MISSING_BUGREPORT.md) and [`docs/ops/LMDE_INSTALLER_DMCRYPT_BUGREPORT_DRAFT.md`](../LMDE_INSTALLER_DMCRYPT_BUGREPORT_DRAFT.md)): one symptom, evidence first, explicit RCA, narrow fix, honest scope of what is and is not changed.

## 6. What this PR does **not** change

- No detector, sampling, RBAC, connector, or report path is touched.
- No CI workflow YAML is touched.
- No regression risk: `.mdc` files are advisory configuration consumed by the agent runtime; if removed, prior behaviour remains intact.
- Zero impact on database locks (no `connectors/sql_sampling.py` change). The customer-database contract from [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) §1–§3 is unaffected.
- No PII, no LAN specifics, no commercial details.

## 7. Doctrine alignment

- [`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md) — paper trail, no silent failure: a refusal-to-grep is a silent demotion of the investigation; this audit names it.
- [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) §2–§3 — when one strategy fails, **degrade with a diagnostic**; do not skip levels. "I will not grep because it is slow" skips levels 1–3 of the fallback hierarchy and emits no diagnostic at all.
- [`AGENT_OVERREACH_RCA_2026-04-27.md`](AGENT_OVERREACH_RCA_2026-04-27.md) — symmetric counterweight: that RCA forbids expanding past stated scope; this one forbids contracting under stated scope on a false excuse.

## 8. Reproduction (for a reviewer)

To verify the speed claim is wrong on this repo, on any reasonable laptop:

```bash
# Whole-tree literal search, capped output. Typically completes in <1s.
rg --hidden --max-count=20 'TODO' .

# Or via the agreed wrapper (Windows / pwsh):
.\scripts\repo-grep.ps1 -Pattern 'TODO' -MaxOutputLines 200
```

The agent's built-in `Grep` tool is the same engine.

## 9. Suggested follow-ups (not in this PR)

- Optional: add a tiny pytest regression guard that asserts the *What not to do* bullet stays present in `operator-investigation-before-blocking.mdc`. Deferred because (a) `.mdc` rules are not currently covered by a guard test today, and (b) doing it in the same PR would expand scope past the symptom — exactly the failure mode of [`AGENT_OVERREACH_RCA_2026-04-27.md`](AGENT_OVERREACH_RCA_2026-04-27.md).
- If the same anti-pattern resurfaces on a different excuse ("file is too large", "directory too deep"), file the next bullet here as a numbered subsection rather than a new file — keep the audit-of-audit Colleague-Nn short.
