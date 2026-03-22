# Operator manual actions (evidence, homelab, study)

**Purpose:** One tracked place for **your** work the agent cannot do: capturing evidence, homelab steps, photos/outputs for context, and **how** study/cert windows sit next to production readiness. No secrets here—put payloads in **`docs/private/`** (gitignored).

**Português (Brasil):** [OPERATOR_MANUAL_ACTIONS.pt_BR.md](OPERATOR_MANUAL_ACTIONS.pt_BR.md)

---

## 1. Study and certification window (2026)

- **Primary focus:** **Paid cyber (CWL)** — complete **BTF** → **C3SA** and the §3.2 list in [PORTFOLIO_AND_EVIDENCE_SOURCES.md](../plans/PORTFOLIO_AND_EVIDENCE_SOURCES.md); **stakeholder proof** = those certs + **shipped Data Boar** + compliance story. The IDE may use **non-Claude** models day to day; Anthropic study is **not** the top priority for **this** project track.
- **Alternating over the year:** **Anthropic Academy** (free; [Anthropic courses](https://docs.claude.com/en/docs/resources/courses)) — sequence in PORTFOLIO §3.0 when you slot AI blocks. **CCA** later when eligible; Skilljar CCA page + unofficial [guide](https://aitoolsclub.com/how-to-become-a-claude-certified-architect-complete-guide/).
- **In parallel (thin thread):** **Priority band A** (Dependabot, Docker Scout, `check-all`)—[PLANS_TODO.md](../plans/PLANS_TODO.md) **–1** / **–1b**.
- **Optional:** Third-party **completion certificates** for CV—not vendor proctored exams.
- **If a CCA attempt does not pass:** Notes in `docs/private/`; **retake** later.

Sequencing rationale also appears in [SPRINTS_AND_MILESTONES.md](../plans/SPRINTS_AND_MILESTONES.md) §3.1 and [PORTFOLIO_AND_EVIDENCE_SOURCES.md](../plans/PORTFOLIO_AND_EVIDENCE_SOURCES.md) §3.0.

---

## 2. Evidence you can collect for the agent (manual)

Do **not** paste passwords or private keys into chat. Prefer:

| Action | Where to put it | Why |
| ------ | ----------------- | --- |
| Homelab inventory (hosts, roles, IPs redacted if needed) | `docs/private/homelab/` per [PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md) | Agent can `read_file` without `@`. |
| Photos of gear, rack, labels (optional) | Same private tree; describe in a `.md` note what each image shows | Visual context for topology discussions. |
| CLI outputs (`ssh`, `curl`, scan summaries) | Paste into a dated note under `docs/private/` or session log | Reproducible debugging. |
| Course / cert completion | PDF or screenshot in `docs/private/`; add a row to PORTFOLIO §3 when you want it on the CV narrative | Keeps thesis/pitch aligned. |

---

## 3. Homelab and validation

- **Criteria:** [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) ([pt-BR](HOMELAB_VALIDATION.pt_BR.md)) §1–§12.
- **What the agent can do:** Suggest commands, read **tracked** docs, read **`docs/private/`** when you maintain it—**not** SSH by itself without your terminal.
- **Operator snapshot for chat:** Keep **`docs/private/WHAT_TO_SHARE_WITH_AGENT.md`** current (gitignored). Layout and hints: [PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md), [docs/private.example/author_info/README.md](../private.example/author_info/README.md).

---

## See also

- [SPRINTS_AND_MILESTONES.md](../plans/SPRINTS_AND_MILESTONES.md) §3.1 — study lane in the sprint picture
- [TOKEN_AWARE_USAGE.md](../plans/TOKEN_AWARE_USAGE.md) — study vs coding same-day discipline
- [OPERATOR_LAB_DOCUMENT_MAP.md](OPERATOR_LAB_DOCUMENT_MAP.md) — which lab doc lives where
