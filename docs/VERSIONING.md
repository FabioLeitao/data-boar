# Version convention and bump checklist

**Português (Brasil):** [VERSIONING.pt_BR.md](VERSIONING.pt_BR.md)

This project uses a **major.minor.build** version scheme:

- **major** – first number (e.g. breaking changes or major release)
- **minor** – second number (e.g. new features, backward-compatible)
- **build** – third number (e.g. fixes, docs, no behaviour change)

Example: `1.3.2` means major 1, minor 3, build 2.

---

## Bump rules

| Bump type | Rule                                                    | Example             |
| ---       | ---                                                     | ---                 |
| **Major** | Increment first number; set minor and build to **0**    | `1.3.2` → **2.0.0** |
| **Minor** | Keep major; increment second number; set build to **0** | `1.3.2` → **1.4.0** |
| **Build** | Keep major and minor; increment build only              | `1.3.2` → **1.3.3** |

---

## Where the version appears (bump checklist)

When you bump the version, update **all** of the following so the number is consistent everywhere:

### 1. Source of truth (required)

| Location             | What to change                                                                                                                                                                                                                                                                                                                |
| ---                  | ---                                                                                                                                                                                                                                                                                                                           |
| **`pyproject.toml`** | Update the `version = "X.Y.Z"` line. This is the **single source of truth** for the installed package. The running application (About page, Report info sheet, heatmap footer, API `/about/json`) reads the version from the installed package metadata, so updating `pyproject.toml` and reinstalling is enough for runtime. |

### 2. Fallback when metadata is missing

| Location            | What to change                                                                                                                                                                    |
| ---                 | ---                                                                                                                                                                               |
| **`core/about.py`** | Update the fallback string in `get_about_info()` when `importlib.metadata.version(...)` fails (e.g. running from source without install). Example: `ver = "1.3.0"` → new version. |

### 3. Man pages

| Location                  | What to change                                                                           |
| ---                       | ---                                                                                      |
| **`docs/lgpd_crawler.1`** | In the `.TH` line (e.g. `"python3-lgpd-crawler 1.3.0"`), set the version to the new one. |
| **`docs/lgpd_crawler.5`** | Same: update the version in the `.TH` line.                                              |

### 4. Deploy and Docker

| Location                    | What to change                                                                                                                                                    |
| ---                         | ---                                                                                                                                                               |
| **`docs/deploy/DEPLOY.md`** | Update any **example** version tags in the Docker tag/push commands (e.g. `1.3.0` in the examples) to the new version so copy-paste commands use the correct tag. |

### 5. Documentation (EN and PT-BR)

| Location                  | What to change                                                                                                                                   |
| ---                       | ---                                                                                                                                              |
| **`README.md`**           | If the text mentions the current version number (e.g. in a release or image tag example), update it.                                             |
| **`README.pt_BR.md`**     | Same as README.md for any explicit version mention.                                                                                              |
| **`docs/USAGE.md`**       | Update any explicit version reference if present.                                                                                                |
| **`docs/USAGE.pt_BR.md`** | Same as USAGE.md.                                                                                                                                |
| **`docs/PLANS_TODO.md`**  | If there is a “current version” or “app version” note in a plan’s “Current state” or publish step, update it when you release.                   |
| **Other docs**            | Search the repo for the old version string (e.g. `1.3.0`) and update any remaining references in SECURITY.md, CONTRIBUTING.md, or release notes. |

### 6. UI and reports (no edit needed if 1–2 are done)

These show the version **dynamically** from package metadata (via `core/about.py`), so they do **not** need manual edits when you bump:

- **About page** (`api/templates/about.html`) – uses `{{ about.version }}`
- **Dashboard / Reports pages** – use `{{ about.version }}`
- **Excel report “Report info” sheet** – `report/generator.py` uses `about["version"]`
- **Heatmap PNG footer** – same `about` dict
- **API `/about/json`** – same `about` dict

After updating `pyproject.toml` (and optionally `core/about.py`), reinstall the package (e.g. `uv sync` or `pip install -e .`) so the new version is in metadata; then the UI and reports will show it automatically.

---

## Quick reference

- **Format:** `major.minor.build`
- **Bump major:** `X.Y.Z` → `(X+1).0.0`
- **Bump minor:** `X.Y.Z` → `X.(Y+1).0`
- **Bump build:** `X.Y.Z` → `X.Y.(Z+1)`
- **Checklist:** pyproject.toml → core/about.py → docs/lgpd_crawler.1, lgpd_crawler.5 → docs/deploy/DEPLOY.md → README (EN/PT-BR), USAGE (EN/PT-BR), PLANS_TODO → search repo for old version string.

**Português (Brasil):** [VERSIONING.pt_BR.md](VERSIONING.pt_BR.md)
