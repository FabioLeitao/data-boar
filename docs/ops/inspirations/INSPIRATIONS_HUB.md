# Inspirations hub (start here)

**Português (Brasil):** [INSPIRATIONS_HUB.pt_BR.md](INSPIRATIONS_HUB.pt_BR.md)

Single **navigation page** for maintainer-chosen **external inputs** that shape Data Boar roadmap, docs tone, and hardening — without becoming automatic policy.

**Folder:** [`docs/ops/inspirations/`](README.md) (this directory).

---

## Security / GRC (hardening, compliance tone, threat framing)

| Document | What it is |
| -------- | ---------- |
| [SECURITY_NOW.md](SECURITY_NOW.md) | Source note: **Security Now** (GRC) — long-running operational security perspective. |
| [OWASP.md](OWASP.md) | OWASP projects and guidance — application security patterns. |
| [CISA_KEV_AND_ADVISORIES.md](CISA_KEV_AND_ADVISORIES.md) | CISA KEV and advisories — patch/exposure prioritization inputs. |
| [QUALYS_THREAT_RESEARCH.md](QUALYS_THREAT_RESEARCH.md) | Qualys TRU / vulnerabilities blog — long-form coordinated disclosure (e.g. AppArmor “CrackArmor”), kernel and infrastructure risk framing. |
| [SECURITY_INSPIRATION_GRC_SECURITY_NOW.md](../SECURITY_INSPIRATION_GRC_SECURITY_NOW.md) | Operator-facing bridge: how we **consume** Security Now–style insight in-repo. |

**People (detailed under Security/GRC):** **Steve Gibson** is the primary public voice behind **Security Now**; full treatment stays in the notes above. A **short pointer** also appears in [ENGINEERING_CRAFT_INSPIRATIONS.md](ENGINEERING_CRAFT_INSPIRATIONS.md) for *explanatory narrative* (not duplicate policy).

---

## Engineering craft (people, products, narrative)

| Document | What it is |
| -------- | ---------- |
| [ENGINEERING_CRAFT_INSPIRATIONS.md](ENGINEERING_CRAFT_INSPIRATIONS.md) | Table of **developers, channels, or products** (sysinternals-style tools, YouTube educators, TiddlyWiki lineage, etc.) with **why it matters** for Data Boar. |
| [ENGINEERING_CRAFT_ANALYSIS.md](ENGINEERING_CRAFT_ANALYSIS.md) | Short **source note**: links the table to the deep analysis (same role as [SECURITY_NOW.md](SECURITY_NOW.md) for Security Now). |
| [ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.md](../ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.md) | **Deep analysis**: thematic clusters, mimic/avoid, workflow, checklist — parallel to [SECURITY_INSPIRATION_GRC_SECURITY_NOW.md](../SECURITY_INSPIRATION_GRC_SECURITY_NOW.md). |

Use this when designing features, operator docs, or “how we explain trade-offs” — still **not** a substitute for threat modeling or tests.

---

## How to extend

1. Add a row to the relevant table file (security note vs engineering table).
1. Keep entries **short**; link out for depth (engineering craft: update [ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.md](../ENGINEERING_CRAFT_INSPIRATION_ANALYSIS.md) when **cross-cutting themes** change, not for every new row).
1. If someone spans both (e.g. security + narrative), put **detail** in Security/GRC notes and a **pointer** in engineering craft if useful.

---

## Related (outside this folder)

- [Operator notification channels](../OPERATOR_NOTIFICATION_CHANNELS.md) — how CI/alerts reach humans (separate from inspiration content).
