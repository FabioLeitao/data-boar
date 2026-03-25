# Suggested full-day plan — lab-op + product (reusable checklist)

**Português (Brasil):** [OPERATOR_NEXT_DAY_CHECKLIST.pt_BR.md](OPERATOR_NEXT_DAY_CHECKLIST.pt_BR.md)

**Purpose:** A **single-day** operator order of work: light **security** maintenance, **homelab** unblocks, optional **–1L** validation, optional **Wabbix** email, and **one** light product slice if energy remains. The agent cannot SSH, use your GitHub session, or touch your hardware.

**Broader context:** [OPERATOR_MANUAL_ACTIONS.md](OPERATOR_MANUAL_ACTIONS.md) · [PLANS_TODO.md](../plans/PLANS_TODO.md) “Resume next session”.

---

## Morning (~2–3h) — security + unblocks

| #  | Activity                                                                                                                                                          | “Done” criterion                                                        |
| -  | --------                                                                                                                                                          | ----------------                                                        |
| M1 | **Band A (–1):** GitHub → **Security → Dependabot** — triage or close **one** item (PR / `pyproject` + `uv lock` + `requirements.txt` + `check-all`)              | One alert handled **or** note “nothing critical today” in private notes |
| M2 | **Band A (–1b):** if you pushed an image recently — `docker scout quickview` on your tag                                                                          | Screenshot or private note if follow-up needed                          |
| M3 | **LAB-OP — `<lab-host-2>` / `pi3b`:** fix `git status` on `homelab-host-report.sh` **or** run `lab-op-sync-and-collect.ps1 -SkipGitPull`                               | New report under `docs/private/homelab/reports/` **or** clean pull      |
| M4 | **ThinkPad T14 + LMDE 7:** continue [LMDE7_T14_DEVELOPER_SETUP.pt_BR.md](LMDE7_T14_DEVELOPER_SETUP.pt_BR.md) through §8 checklist **or** record where you stopped | One line in private notes                                               |

---

## Afternoon (~3–4h) — validation or external comms

| #  | Activity                                                                                                                                                     | “Done” criterion                                                                     |
| -  | --------                                                                                                                                                     | ----------------                                                                     |
| T1 | **Order –1L:** on **one** lab host, [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) §1.1–1.2 + §2 synthetic **or** §1.3–1.5 Docker if containers already work | Dated note with pass/fail; paste outputs to `docs/private/` if you want agent review |
| T2 | **Wabbix (optional):** send baseline email using [WABBIX_IN_REPO_BASELINE.md](WABBIX_IN_REPO_BASELINE.md) + cite `WABBIX_ANALISE_2026-03-18.md`              | Sent **or** draft saved with send date                                               |
| T3 | **Read-only:** skim [PLAN_LAB_OP_OBSERVABILITY_STACK.md](../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.md) §1 — pick **A or B** + **C or D** later                | One sentence in private runbook                                                      |

---

## Late afternoon / light evening (≤1h)

| #  | Activity                                                                                                       | “Done” criterion                    |
| -  | --------                                                                                                       | ----------------                    |
| N1 | Refresh **`docs/private/WHAT_TO_SHARE_WITH_AGENT.md`**                                                         | File saved                          |
| N2 | If **SNMP Task Scheduler** runs — tail latest `snmp_udm_probe_*.log`                                           | Glance OK/errors                    |
| N3 | **One** product slice only if energy left: see “What to start next” in [PLANS_TODO.md](../plans/PLANS_TODO.md) | Named issue/branch for next morning |

---

## What the agent **cannot** do for you

- SSH to hosts, `sudo` on your T14, log into GitHub as you.
- Send Wabbix email — can only draft text.
- Decide laptop RAM for Grafana/Graylog — you measure and document.

---

**Tip:** Next chat: *“Follow OPERATOR_NEXT_DAY_CHECKLIST; done M1–M3; blocked on M4 because …”*.
