# Dependabot: Pygments CVE-2026-4539 (upstream patch pending)

**Context:** **`pip-audit`** and GitHub **Dependabot** may flag **pygments** at **2.19.2** with **CVE-2026-4539** (inefficient regex in **`AdlLexer`**, local-access / ReDoS class issue).

**Why we cannot bump yet:** As of the last check, **PyPI’s latest release is still 2.19.2** — there is **no newer version** that resolves the advisory. The project keeps **`pygments>=2.19.2`** in **`pyproject.toml`** so installs stay on the current latest.

**Residual risk (operator judgment):** Data Boar uses **Pygments** for **syntax highlighting** in CLI/UX paths, not for untrusted remote lexer selection in typical deployments. Treat as **monitor and upgrade when PyPI publishes a fix**.

**When a fix ships:**

1. Raise **`pygments`** floor in **`pyproject.toml`** to the patched release.
2. Run **`uv lock`**, **`uv export --no-emit-package pyproject.toml -o requirements.txt`**, **`.\scripts\check-all.ps1`**.
3. Merge; re-run **`pip-audit -r requirements.txt`**.

**Optional GitHub UI:** Maintainers may **dismiss** the alert with **`patch_unavailable`** and a comment linking this doc — **recheck** after each **pygments** release on PyPI.

**Related:** [SECURITY.md](../SECURITY.md), [DEPENDABOT_PYOPENSSL_SNOWFLAKE.md](DEPENDABOT_PYOPENSSL_SNOWFLAKE.md).
