# Plan: Opt-in network port / service hints (“hidden ingredients” adjacent)

**Status:** Proposal (not implemented)
**Synced with:** [PLANS_TODO.md](PLANS_TODO.md), [PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md](PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md) (Tier 3b / “sniffing for hidden ingredients” umbrella)

## Purpose

Offer an **optional**, **explicitly authorized** capability to probe **already-in-scope or operator-declared** hosts and well-known ports for **lightweight service hints** (e.g. TCP connect + short read / banner-style string, **not** a full port sweep or exploit toolkit). Goal: help teams discover **shadow IT** or **legacy systems** that may hold personal data but were omitted from the formal inventory (“forgotten soup ingredients”), while staying compatible with **zero-trust**, **least privilege**, and **clear contractual scope**.

## Alignment with the product

- **On brand:** Fits the **data soup** narrative—expand **known ingredients** without claiming omniscience. Output is **hints and inventory classifiers**, not legal verdicts.
- **Different from core Boar:** Today the product **ingests configured targets** (DBs, paths, APIs). This plan adds a **bounded network reconnaissance adjunct** that only runs when the operator enables it and constrains scope.
- **Not a replacement for nmap / ASV / pentest:** Scope is **narrow** (allowed hosts + allowlisted ports + rate limits + timeouts). **No** default internet-wide discovery, **no** exploitation, **no** credential stuffing.

## Zero-trust / min-privilege design principles

1. **Default off:** No probes unless `discovery.network_port_hints.enabled` (name TBD) is true and scope is non-empty.
2. **Positive allowlists only:** Targets must be **explicit**—e.g. list of IPs/hostnames **and/or** CIDR ranges **declared in config** (or CLI), **not** “scan the whole VPC” unless the customer pastes that range deliberately.
3. **Separate from auth to data:** Port hints do **not** bypass database auth; they may suggest “something listens like MySQL” so the operator can **add a proper target** for a full scan.
4. **Rate and concurrency caps:** Hard limits on concurrent connects, total probes per run, and per-host cool-off to avoid looking like DoS.
5. **Auditability:** Log each probe (host, port, outcome, bytes read cap) in existing operator/audit surfaces; include in exported audit trail when that matures.
6. **Enterprise / advanced SKU (optional):** Candidate for **licensed feature pack** (see [LICENSING_SPEC.md](../LICENSING_SPEC.md)); open-core could stay “disabled stub” or “docs only” until policy is set.

## Stakeholders, compliance, and legal

| Audience | What to communicate |
| -------- | ------------------- |
| **Customer decision-makers / IT** | This is **optional asset-discovery support**, scoped by them; outputs are **technical hints** for inventory completeness, not certification of compliance. |
| **DPO / privacy** | Probing may reveal **existence** of services that process personal data; treat as **processing metadata** about infrastructure. **Data minimisation:** banner-only or first-N-byte read; **no** storage of raw payloads beyond short hashes/snippets in logs if policy requires redaction. |
| **Security / SOC** | Coordinate so probes are **expected** on the network; wrong timing can trigger IDS/IPS. Document **source IP** (scanner host) and **schedule**. |
| **Legal / SOW** | **Written authorization** for the exact scope (IPs/ports/time window) is mandatory before enabling in regulated engagements. Do not market as covert discovery. |

**Product copy:** Avoid language that suggests **evading** customer oversight or “catching them hiding.” Prefer **inventory completeness**, **shadow IT awareness**, and **operator-controlled scope**.

## Proposed technical phases

| Phase | Deliverable | Status |
| ----- | ----------- | ------ |
| 1 | **Config schema + guardrails:** `discovery.network_port_hints` (or under `targets`-adjacent block): `enabled`, `hosts[]`, `cidrs[]` (optional), `ports[]` (allowlist), `connect_timeout_ms`, `read_max_bytes`, `max_probes_per_run`, `concurrency`. Reject ambiguous “wide” defaults. | ⬜ Pending |
| 2 | **Engine module:** Async or threaded TCP connect with timeout; optional single **read** for banner; map (port, prefix) → **hint label** (e.g. “likely HTTP”, “likely PostgreSQL”, “unknown TCP”). No protocol full parses in v1. | ⬜ Pending |
| 3 | **Outputs:** New report section or sheet row “**Network service hints**” (host, port, hint, evidence excerpt redacted); link to **Data source inventory** where applicable. | ⬜ Pending |
| 4 | **CLI / dashboard:** Toggle mirroring other heavy features (`--network-port-hints` or dashboard checkbox) with **WARNING** in stdout/stderr when enabled. | ⬜ Pending |
| 5 | **Tests:** Unit tests with localhost mock listener; no flaky real-network dependency in CI. | ⬜ Pending |
| 6 | **Docs:** USAGE + SECURITY (authorized use, IDS notice) + pt-BR sync; cross-link from [SECURITY.md](../SECURITY.md). | ⬜ Pending |

## Risks

- **Misuse:** Operators run wide scans without permission → **mitigate** with allowlist-only schema and loud UI warnings.
- **Noise:** Many ports open in prod → **mitigate** with small default port sets and “suggest targets” UX rather than auto-adding credentials.
- **Liability perception:** “Like nmap” → **position** as **inventory helper** with explicit scope; defer aggressive techniques indefinitely.

## Cross-references

- **Tier 3b / hidden ingredients:** [PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md](PLAN_ADDITIONAL_DATA_SOUP_FORMATS.md) § Tier 3b and Tier 4 (network strings **inside** files vs this plan: **live** port hints).
- **Data source inventory:** Existing report sheet can reference hinted services once a real target is configured.
- **Dashboard HTTPS / trust:** Transport and audit posture in [PLAN_DASHBOARD_HTTPS_BY_DEFAULT_AND_HTTP_EXPLICIT_RISK.md](PLAN_DASHBOARD_HTTPS_BY_DEFAULT_AND_HTTP_EXPLICIT_RISK.md).
