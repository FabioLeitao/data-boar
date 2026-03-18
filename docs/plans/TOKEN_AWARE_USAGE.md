# Token-aware usage – short and long-term goals

**Purpose:** Keep progress effective when **token/context limits** apply (e.g. after an initial Pro+ burst). Use this doc and [PLANS_TODO.md](PLANS_TODO.md) as the main entry points so sessions stay focused and avoid loading the whole repo.

**Policy:** Prefer **one plan or one feature at a time**; open only the files needed for that slice. Update PLANS_TODO and the relevant plan file when a step is done.

---

## 1. Short-term vs long-term (at a glance)

| Horizon | Focus | Where it lives |
| --------| ----- | --------------- |
| **Short (this cycle)** | High-value, small-scope slices: CNPJ Phase 4–5, Content-type steps 2–6, FN reduction (MEDIUM threshold + wording), Strong crypto Phase 1, Data source inventory Phase 1, Notifications Phase 1. | PLANS_TODO § “What to start next”, § “A. Near-term focus” |
| **Medium** | Readiness: runbooks, compliance evidence subsection, data retention note, onboarding checklist, dependency policy sentence. | [PLAN_READINESS_AND_OPERATIONS.md](PLAN_READINESS_AND_OPERATIONS.md) |
| **Long (academic)** | Lato sensu thesis (framing, case studies, evidence mapping); stricto sensu research path; compliance evidence mapping table. | [PLAN_LATO_SENSU_THESIS.md](PLAN_LATO_SENSU_THESIS.md), [PLAN_STRICTO_SENSU_RESEARCH_PATH.md](PLAN_STRICTO_SENSU_RESEARCH_PATH.md), [PLAN_COMPLIANCE_EVIDENCE_MAPPING.md](PLAN_COMPLIANCE_EVIDENCE_MAPPING.md) |
| **Deferred / backlog** | Secrets Phase B, Version check, Selenium QA, Synthetic data, SAP, Dashboard i18n, Additional data soup formats. | PLANS_TODO § “B. Deferred”, § “C. Backlog” |

---

## 2. Working under token constraints

- **Single-context rule:** For each session, choose **one** of: (a) one plan’s next to-do, (b) one readiness item, or (c) one academic-plan section. Open only that plan file + the code/docs files you need to edit.
- **Entry point:** Start from [PLANS_TODO.md](PLANS_TODO.md). Use the “What to start next” table and the “Order” column to pick the next step.
- **AI-heavy vs manual-friendly:** PLANS_TODO marks which tasks benefit from AI (research, wording, design) vs which you can do by hand (regex wiring, tests, config). Use AI for the former; do the latter in small, focused sessions.
- **After each step:** Run `uv run pytest -v -W error` (or `.\scripts\check-all.ps1` on Windows), update the plan and PLANS_TODO, then commit. Avoid stacking many uncommitted changes.

---

## 3. Artifacts and evidence (for narrative and thesis)

**Full checklist (URLs, Dockerfiles, GitHub, certifications, community):** [PORTFOLIO_AND_EVIDENCE_SOURCES.md](PORTFOLIO_AND_EVIDENCE_SOURCES.md). Use it when drafting thesis, evidence mapping, or pitch so you open one source at a time.

Summary:

- **This repo (Data Boar):** Main compliance/LGPD artifact; Docker image `fabioleitao/data_boar`; Dockerfile in repo root.
- **Docker Hub:** Public pages fetched for data_boar, wildfly_t1r, uptk (tags, sizes, links). Authoritative list: `docs/private/From Docker hub list of repositories.md`.
- **GitHub:** FabioLeitao/data-boar, wf_t1r, and other public repos; profile and repo list in PORTFOLIO_AND_EVIDENCE_SOURCES.
- **Certifications / community:** LPIC-1 (101); Ubuntu tester/collaborator. Add others in PORTFOLIO_AND_EVIDENCE_SOURCES §3.
- **Private docs (git-ignored):** CV, TCC, LinkedIn PDFs in `docs/private/`; reference by filename only.

Optional: add Dockerfiles (or a short note) for wildfly_t1r/uptk in `docs/private/Dockerfiles_used.md` or in the wf_t1r repo so “Dockerfiles I created and used” is easy to cite.

When you add new evidence, list it in PORTFOLIO_AND_EVIDENCE_SOURCES or in this section so the next session knows what to use.

---

## 4. One-session recipe (example)

1. Open **PLANS_TODO.md** and pick one row from “What to start next” (e.g. Content-type Step 2).
2. Open **PLAN_CONTENT_TYPE_AND_CLOAKING_DETECTION.md** and the one or two source files you need (e.g. config schema, filesystem connector).
3. Implement the step; add tests; update USAGE or TECH_GUIDE if needed.
4. Mark the to-do done in both the plan and PLANS_TODO; run tests; commit.
5. Next session: repeat with the next row or the next step in the same plan.

---

## 5. Sync and maintenance

- **PLANS_TODO** is the single source of truth for execution order and status. When a plan file’s to-dos change, sync PLANS_TODO so the “What to start next” table and open-plan sections stay accurate.
- This file (TOKEN_AWARE_USAGE) should be updated when: (1) short vs long-term priorities change, (2) a new artifact or doc is added to `docs/private/`, or (3) you adopt a new “one-session” pattern.
