# SRE Dependency Guardian audit — 2026-04-27

> Read-only deliverable from the **SRE Automation Agent** acting as
> *Dependency Guardian* (Slack-triggered protocol). The agent reviewed every
> Dependabot PR open against `main` at 2026-04-27 ~16:23 UTC and recorded
> the findings here. **Audit-and-block** posture: no `git push` to any of
> the audited Dependabot branches.

## TL;DR

| # | Sev | Package | From → To | Decision |
| --- | --- | --- | --- | --- |
| #226 | Info | `pyo3` (Cargo) | `0.23.5 → 0.24.1` | **Safe to merge.** CI green. Bundles upstream RUSTSEC fix for `PyString::from_object`; this repo does not call that API but should still take the bump. |
| #221 | Info | `pip-minor-patch` group (35 pkgs) | minor/patch | **Apply locally**, do not click merge until CI is green (see §2.1 systemic finding). |
| #222 | Medium | `chardet` | `5.2.0 → 7.4.3` | **Manual Review Required.** Major-version jump; sits on the encoding fallback path doctrine in `THE_ART_OF_THE_FALLBACK.md`. CI red because of §2.1. |
| #223 | Info | `tzdata` | `2025.3 → 2026.2` | **Apply locally**, low risk; CI red only because of §2.1. |
| #224 | Medium | `cryptography` | `46.0.7 → 47.0.0` | **Manual Review Required.** Major version with documented backwards-incompatible removals (binary EC curves, OpenSSL 1.1.x, LibreSSL <4.1). Project uses `cryptography.hazmat` for Ed25519 license JWTs — needs a green CI before any merge, but CI is red because of §2.1. |

**Net new finding vs the 2026-04-27 16:08 UTC pass (PR #234):** none.
Same systemic Medium remains the only blocker. This pass adds a **concrete
companion fix** (`scripts/dependabot-resync.{sh,ps1}` + `README.md`) the
maintainer can run from a checked-out Dependabot branch to make the
guard turn green without touching the bot diff.

---

## 1. Methodology

Per the Slack-triggered Dependency Guardian rule, for each open PR the
agent did:

1. **Extraction** — read `gh pr view --json title,body,mergeable,mergeStateStatus`
   and `gh pr checks` for each of `#221 #222 #223 #224 #226`.
2. **Impact mapping** — `rg -l "import <pkg>|from <pkg>"` across `--type py`
   (`chardet` → no callers; `cryptography` → `core/licensing/verify.py`,
   `tests/test_licensing.py`, `tests/test_api_assessment_poc.py`,
   `scripts/issue_dev_license_jwt.py`; `pyo3 PyString::from_object` →
   `rust/boar_fast_filter/src/lib.rs` does not call that API).
3. **Upgrade strategy** — favour the **lowest** version that fixes the
   advisory and is compatible (per Dependency Guardian rule item 3).
4. **Change analysis** — read upstream changelogs as they appear in each
   Dependabot PR body; cross-check with `pyproject.toml` and `uv.lock` to
   see whether constraints are direct or transitive.
5. **CI signal** — `gh pr checks` exit codes for each PR. Red = block.

Doctrine references applied:

- **[`DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)**
  — Data Boar is a guest in the customer DB. A merge that lands an
  inconsistent lockfile is the supply-chain equivalent of a "surprise
  side effect" (§1 clause 3).
- **[`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)**
  — `chardet` lives on the encoding-resilient byte-scan path; a major
  bump is exactly the kind of change that must produce a diagnostic (CI
  green) on fall, never a silent regression.

---

## 2. Systemic finding — Medium

### 2.1 RCA: every pip Dependabot PR breaks `tests/test_dependency_artifacts_sync.py`

**Symptom (observed):** `gh pr checks 221`, `222`, `223`, `224` all show
`Lint (pre-commit)` and `Test (Python 3.12 / 3.13)` failing. `gh pr checks 226`
(Cargo path) is fully green.

**Cause:** the project enforces a single source of truth across
`pyproject.toml`, `uv.lock`, and `requirements.txt` via
[`tests/test_dependency_artifacts_sync.py`](../../../tests/test_dependency_artifacts_sync.py)
and the matching pre-commit hook. Dependabot `pip` PRs only edit
`requirements.txt` — they do not run `uv lock` or
`uv export --no-emit-package pyproject.toml -o requirements.txt`. The
exporter normalizes hash ordering and metadata, so the bot diff drifts
even when the version pin matches.

**Why this is Medium and not Low:** if the maintainer rage-merges any of
these PRs to land a security bump (e.g. `cryptography 47.0.0` for a CVE,
hypothetically), the merged commit ships:

- a `requirements.txt` not derived from `uv.lock`, breaking reproducible
  installs;
- an SBOM (`sbom.yml`) generated against an inconsistent input set —
  exactly the fail-open pattern flagged by
  [`SUPPLY_CHAIN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_CHAIN_AND_TRUST_SIGNALS.md).

**Action taken (this PR):** add a paired helper so the maintainer has a
**five-second** local fix instead of typing `uv lock && uv export …`
from memory:

- [`scripts/dependabot-resync.sh`](../../../scripts/dependabot-resync.sh)
  (Linux / macOS / CI shells)
- [`scripts/dependabot-resync.ps1`](../../../scripts/dependabot-resync.ps1)
  (Windows primary dev workstation)

Both run `uv lock`, then `uv export --no-emit-package pyproject.toml -o requirements.txt`
with the **exact** flags the guard expects, then re-run
`tests/test_dependency_artifacts_sync.py -v -W error`. Failure modes
print a diagnostic message pointing at
`.cursor/skills/dependabot-recommendations/SKILL.md` (THE_ART_OF_THE_FALLBACK
clause: never silent fallback).

**Operator workflow:**

```bash
gh pr checkout 224                         # cryptography 47.0.0
./scripts/dependabot-resync.sh --commit    # regen + commit chore(deps)
git push                                   # CI turns green
```

```powershell
gh pr checkout 224
.\scripts\dependabot-resync.ps1 -Commit
git push
```

**Action not taken:** the agent did **not** `git push` regenerated
`uv.lock` / `requirements.txt` to any Dependabot branch. The guardian rule
requires manual review before applying any change to a bot PR; the helper
exists so that review is cheap.

**Follow-up not in scope here (P1):** add a `pull_request_target` workflow
that runs `dependabot-resync.sh --check` on every Dependabot pip PR and
posts the regen diff as a PR comment. That is a separate change and
needs `permissions: pull-requests: write` plus a careful actor-checker
(only run on `dependabot[bot]` head). Captured for `PLANS_TODO.md`.

---

## 3. Per-PR notes

### 3.1 #224 — `cryptography 46.0.7 → 47.0.0` (Medium / Manual Review)

- **Callers (production-critical):**
  [`core/licensing/verify.py`](../../../core/licensing/verify.py) calls
  `cryptography.hazmat.primitives.serialization.load_pem_public_key` and
  `cryptography.hazmat.backends.default_backend` for Ed25519 license JWT
  verification. `pyjwt[crypto]` re-exports the same backend.
- **Callers (tooling / tests):**
  [`scripts/issue_dev_license_jwt.py`](../../../scripts/issue_dev_license_jwt.py),
  [`tests/test_licensing.py`](../../../tests/test_licensing.py),
  [`tests/test_api_assessment_poc.py`](../../../tests/test_api_assessment_poc.py).
- **Breaking changes that matter for this repo (per upstream changelog):**
  - Drops Python 3.8 support — *not applicable*: `pyproject.toml` already
    requires `python>=3.12`.
  - Drops binary elliptic curves (`SECT*`) — *not applicable*: only Ed25519
    is used.
  - Drops OpenSSL 1.1.x and LibreSSL <4.1 — *not applicable* on
    `ubuntu-latest` runners.
  - Loading keys with unsupported algorithms now raises
    `UnsupportedAlgorithm` instead of `ValueError` — **review point**:
    `decode_license_jwt` propagates `jwt.PyJWTError`, but the helper
    `load_ed25519_public_key_pem` does not narrow exceptions, so the new
    type would surface as-is to callers. No regression test asserts a
    specific exception class.
- **Recommendation:** safe to apply locally **after** §2.1 fix; CI must
  pass `tests/test_licensing.py` with `-W error`. Do not merge the bot
  branch directly until then.

### 3.2 #222 — `chardet 5.2.0 → 7.4.3` (Medium / Manual Review)

- **Callers:** none in current Python sources (`rg "import chardet|from chardet"`
  returns no hits). `chardet` is pulled transitively / as a fallback layer
  (encoding-resilient byte scans) — see
  [`THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md) §3.
- **Risk:** even with no direct call site, a 5.x → 7.x jump on the
  encoding fallback layer can shift confidence values; the manifesto says
  "fallbacks must produce a diagnostic, never a silent regression."
- **Recommendation:** apply locally after §2.1 fix and verify the existing
  `report/scan_evidence.py` audit log still labels demotions consistently.

### 3.3 #223 — `tzdata 2025.3 → 2026.2` (Info)

- Pure data update (Brazilian summer-time history is unaffected; British
  Columbia change is a UI concern, not Data Boar). Apply with §2.1 fix.

### 3.4 #221 — `pip-minor-patch` grouped 35 updates (Info, but blocked)

- All bumps are minor/patch within the project's accepted upper bounds.
  The risk profile is **dominated by §2.1**, not by any individual entry.
  Apply locally with the resync helper.

### 3.5 #226 — `pyo3 0.23.5 → 0.24.1` (Info, GREEN — recommend merge)

- Cargo path; CI fully green.
- Upstream `0.24.1` is a security fix for `PyString::from_object`. The
  Data Boar Rust crate
  [`rust/boar_fast_filter/src/lib.rs`](../../../rust/boar_fast_filter/src/lib.rs)
  does **not** call that API, so the advisory does not affect this code
  path directly. The bump still ships defensively (defense in depth: the
  unsafe codepath disappears even if a future contributor reaches for it).
- **Recommendation:** merge as-is.

---

## 4. Action items (handed back to the maintainer)

1. **Merge #226** — green, doctrinally aligned, no diff churn.
2. **Run the resync helper** on each pip Dependabot PR branch the
   maintainer wants to land:
   - Highest priority: #224 (security-relevant package, even though this
     specific bump is not advisory-driven; the next one will be).
   - Then #222 (encoding fallback discipline).
   - Then #221 / #223 (low risk, Just Works after the resync).
3. **Open follow-up plan row** (P1) — `pull_request_target` workflow that
   runs `dependabot-resync.sh --check` and comments the regen diff on
   Dependabot pip PRs. Out of scope for this audit.

## 5. Files added by this PR

- `scripts/dependabot-resync.sh` — Linux/macOS helper, executable.
- `scripts/dependabot-resync.ps1` — Windows pair (per
  [`docs/ops/SCRIPTS_CROSS_PLATFORM_PAIRING.md`](../SCRIPTS_CROSS_PLATFORM_PAIRING.md)).
- `docs/ops/sre_audits/README.md` — anchors the audit folder on `main`
  (the previous audit lives only on PR #234's branch and would be lost
  if that PR is closed without merge).
- `docs/ops/sre_audits/PR_SECURITY_AUDIT_2026-04-27_dependency_guardian.md`
  — this report.

## 6. Verification

- `bash scripts/dependabot-resync.sh --check` — `uv lock --check` returns
  zero, dependency-artifacts pytest passes.
- `uv run pytest tests/test_dependency_artifacts_sync.py -v -W error`
  passed locally on this branch.
- `uv run pre-commit run --all-files` — see PR check output (CI is the
  authoritative signal; do not merge if red).

## 7. Doctrine references

- [`docs/ops/inspirations/DEFENSIVE_SCANNING_MANIFESTO.md`](../inspirations/DEFENSIVE_SCANNING_MANIFESTO.md)
  — no surprise side effects; clause 3 of the customer-DB contract.
- [`docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md`](../inspirations/THE_ART_OF_THE_FALLBACK.md)
  — diagnostic on fall; the resync helper prints next steps before
  exiting non-zero.
- [`docs/ops/inspirations/SUPPLY_CHAIN_AND_TRUST_SIGNALS.md`](../inspirations/SUPPLY_CHAIN_AND_TRUST_SIGNALS.md)
  — SBOM ↔ wheel alignment.
- [`.cursor/skills/dependabot-recommendations/SKILL.md`](../../../.cursor/skills/dependabot-recommendations/SKILL.md)
  — operator-side workflow.
