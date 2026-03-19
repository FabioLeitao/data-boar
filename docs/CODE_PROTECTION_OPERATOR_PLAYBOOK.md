# Code protection & commercial hygiene — operator playbook

**Português (Brasil):** [CODE_PROTECTION_OPERATOR_PLAYBOOK.pt_BR.md](CODE_PROTECTION_OPERATOR_PLAYBOOK.pt_BR.md)

**Purpose:** Give you **concrete phrases** to steer an AI assistant (or a human operator) through **safety, IP exposure, and profitability guardrails** without burning context on unrelated features. This complements [PLANS_TODO.md](plans/PLANS_TODO.md) **Priority band A** and [TOKEN_AWARE_USAGE.md](plans/TOKEN_AWARE_USAGE.md) §6.

**Rule:** One **step** (A1–A7) per session unless a step is trivially short. After **A1–A3**, you may resume **token-aware** feature work unless A4–A7 block revenue or compliance.

---

## Phase map (order)

| Phase | ID | You do | Agent helps with |
| ----- | -- | ------ | ------------------ |
| **Dependencies** | A1 | Approve/merge Dependabot PRs on GitHub | Triage alerts, bump pins, run tests, fix breakages |
| **Image CVEs** | A2 | Run Docker locally, approve Dockerfile changes | `docker scout` output interpretation, minimal base image / pin bumps |
| **Public registry** | A3 | Docker Hub UI: delete or document tags | Update [deploy/DEPLOY.md](deploy/DEPLOY.md) §8, Compose/K8s refs |
| **Issuer isolation** | A4 | Create private repo; copy `tools/license-studio`; **never** push keys | Private README template, checklist, `.gitignore` reminders |
| **People** | A5 | GitHub/GitLab invites for partners | — |
| **Automation** | A6 | Approve CI additions | `scripts/license-smoke.ps1` or pytest job, docs only in one PR |
| **Legal** | A7 | Call counsel | Doc pointers: [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](LICENSING_OPEN_CORE_AND_COMMERCIAL.md) |

---

## Copy-paste prompts (control what you ask)

Use these **verbatim** or tweak the bracketed parts.

### A1 — Dependabot / dependency hygiene

> **Priority band A, step A1 only.** Open GitHub Security → Dependabot for this repo. List open alerts by severity. For each safe upgrade, propose the minimal change to `pyproject.toml` / lockfiles / `requirements.txt` so `.\scripts\check-all.ps1` stays green. Do **not** start feature work.

### A2 — Docker Scout / image hardening

> **Priority band A, step A2 only.** Review the root `Dockerfile` for unnecessary packages and outdated base tags. Assume I can run `docker scout quickview` locally — tell me exactly what to run and how to interpret HIGH/CRITICAL. Propose the smallest Dockerfile diff; run no unrelated refactors.

### A3 — Docker Hub tag lifecycle

> **Priority band A, step A3 only.** Compare [DEPLOY.md](deploy/DEPLOY.md) §8 with a tag list I paste from Docker Hub. Tell me which tags are safe to delete vs which must stay for partners/CI. Update DEPLOY.md + DEPLOY.pt_BR.md supported-tag wording to match; do not change application code.

### A4 — Private issuer repo (no secrets in public)

> **Priority band A, step A4 only.** Draft a **private-repo** README outline for copying `tools/license-studio` out of the public tree: directory layout, how to build `sign`, where keys live (never in git), and link to [LICENSING_SPEC.md](LICENSING_SPEC.md). No keys, no real URLs with tokens.

### A5 — Partner access (manual)

> You do this without the agent: add collaborators on the **private** issuer repo and any other private assets. Do not paste secrets into chat.

### A6 — License smoke test / CI hook

> **Priority band A, step A6 only.** Add or extend `scripts/license-smoke.ps1` (or a single pytest module) that proves **open** mode still starts and **enforced** mode fails fast without a valid `.lic` in a temp config. Document usage in [TESTING.md](TESTING.md) in a short subsection. One focused PR.

### A7 — Legal boundary (manual + counsel)

> **Priority band A, step A7.** (You + lawyer.) Agent may only: point to [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](LICENSING_OPEN_CORE_AND_COMMERCIAL.md) and [LICENSING_SPEC.md](LICENSING_SPEC.md); do not draft binding legal text.

---

## Returning to token-aware pace

When A1–A3 are done (and nothing is on fire), say:

> **Resume token-aware pace.** Next row only from [PLANS_TODO.md](plans/PLANS_TODO.md) “What to start next” — pick order **[N]** and do not load other plans.

---

## Related docs

- [PLANS_TODO.md](plans/PLANS_TODO.md) — Priority band A table + execution order
- [TOKEN_AWARE_USAGE.md](plans/TOKEN_AWARE_USAGE.md) — one-session discipline
- [LICENSING_SPEC.md](LICENSING_SPEC.md) — runtime token behaviour
- [HOSTING_AND_WEBSITE_OPTIONS.md](HOSTING_AND_WEBSITE_OPTIONS.md) — public vs private hosting costs
- [RELEASE_INTEGRITY.md](RELEASE_INTEGRITY.md) — signed release manifest (optional)
