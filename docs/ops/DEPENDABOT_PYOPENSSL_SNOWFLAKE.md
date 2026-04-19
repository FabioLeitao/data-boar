# Dependabot: pyOpenSSL alerts blocked by Snowflake connector pin

**Context:** GitHub Dependabot may show **open** alerts **#9** and **#10** for **pyOpenSSL** (CVE-2026-27448 low, CVE-2026-27459 high). The fix is **pyOpenSSL ≥ 26.0.0**.

**Why we cannot bump yet:** **`pyopenssl`** is pulled in as a **transitive** dependency of **`snowflake-connector-python`** ([`bigdata` optional extra](../../pyproject.toml)). Published **`snowflake-connector-python`** versions (through **4.3.0** on PyPI) declare **`pyopenssl<26`**, so **`uv lock`** cannot resolve **`pyopenssl>=26`** together with **`data-boar[bigdata]`** without an unsatisfiable graph.

**Upstream:** Snowflake is aware (e.g. [snowflake-connector-python#2789](https://github.com/snowflakedb/snowflake-connector-python/issues/2789)) — watch for a connector release that relaxes the upper bound to allow **pyOpenSSL 26+**, then:

1. Bump **`snowflake-connector-python`** (or add an explicit **`pyopenssl>=26.0.0`** floor if the connector no longer caps it).
1. Run **`uv lock`**, **`uv export --no-emit-package pyproject.toml -o requirements.txt`**, **`.\scripts\check-all.ps1`**.
1. Merge; Dependabot should close **#9** / **#10** when the lockfile no longer contains a vulnerable range.

**Risk note (operator judgment):** The advisories concern **DTLS cookie callbacks** and **SNI callback exception handling**. Typical Data Boar use of the Snowflake connector does not custom-wire these OpenSSL callbacks; residual risk is lower than the raw CVSS suggests for many deployments, but the lockfile remains in GitHub’s “vulnerable range” until upstream ships.

**Optional GitHub UI:** If noise is high, maintainers may **dismiss** alerts with reason **`patch_unavailable`** and a comment linking this doc — **re-open or re-check** when the connector releases.

**Related:** [SECURITY.md](../SECURITY.md) (dependency workflow), [MAINTENANCE_FRONT_OF_WORK.md](../plans/MAINTENANCE_FRONT_OF_WORK.md) (S4 / A1). **`.\scripts\maintenance-check.ps1`** (after `gh auth login`) lists open Dependabot **alerts** and points here for pyOpenSSL/Snowflake context.
