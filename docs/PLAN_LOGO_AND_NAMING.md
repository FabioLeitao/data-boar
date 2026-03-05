# Logo, favicon, and application naming recommendations

**Status:** In progress
**Synced with:** [docs/PLANS_TODO.md](PLANS_TODO.md) (central to-do list)

Plan for a copyright-safe logo (web, favicon, optional report), integration points in the app, and alternative application names (e.g. compliance_crawler) with availability notes for you to decide.

---

## To-dos

Mark items done here and in [PLANS_TODO.md](PLANS_TODO.md) when actually completed.

| #   | To-do                                                                                                                                              | Status    | Notes                                                    |
| --- | ---                                                                                                                                                | ---       | ---                                                      |
| 1   | Decide logo concept (A–D) and colors; produce master logo (SVG) and export web PNG (32/64 px) and favicon (ICO or 16/32 PNG)                       | ⬜ Pending | Copyright-safe, scales to 16 px                          |
| 2   | Place assets in `api/static/`: favicon.ico (and/or favicon-32.png), logo.svg, logo-64.png                                                          | ⬜ Pending | Optional: logo-report-48.png for Excel                   |
| 3   | Add favicon link(s) in `api/templates/base.html` (`<link rel="icon">`)                                                                             | ⬜ Pending | Browser/tab icon                                         |
| 4   | (Optional) Add logo to About page and optionally Dashboard/Reports header                                                                          | ⬜ Pending | `api/templates/about.html`, dashboard.html, reports.html |
| 5   | Check PyPI and web for chosen name (e.g. compliance_crawler) availability                                                                          | ⬜ Pending | Avoid clashes with existing products                     |
| 6   | Decide display name and/or package rename; if changing, update `core/about.py` and/or `pyproject.toml` and docs per [VERSIONING.md](VERSIONING.md) | ⬜ Pending | Display name only = no package rename                    |
| 7   | (Optional) Embed logo in Excel Report info sheet via `report/generator.py`                                                                         | ⬜ Pending | openpyxl image at fixed cell                             |
| 8   | (Optional) Add logo to heatmap PNG footer in `_create_heatmap`                                                                                     | ⬜ Pending | Small image via matplotlib                               |

**Sync:** When a step is actually done, mark it **✅ Done** in this table and in the same row in [PLANS_TODO.md](PLANS_TODO.md) so both files stay in sync.

---

## Current state

- **Package / display name:** `python3-lgpd-crawler` ([core/about.py](../core/about.py), [pyproject.toml](../pyproject.toml)).
- **No logo or favicon today:** [api/templates/base.html](../api/templates/base.html) has no `<link rel="icon">`; static assets live in [api/static/](../api/static/) (style.css, app.js, dashboard.js).
- **Report:** "Report info" sheet is a Field/Value table; heatmap footer is text-only ([report/generator.py](../report/generator.py) `_build_report_info`, heatmap in `_create_heatmap`).
- **Audience and scope:** DPO/compliance teams; PII/sensitive data auditing across DBs and filesystems; LGPD, GDPR, CCPA, HIPAA, GLBA; scanning, mapping, reporting.

---

## 1. Logo concept (copyright-safe and on-message)

**Goal:** One simple, original mark that works at **favicon size (16–32 px)**, **web (e.g. 32–64 px)**, and **report (e.g. 24–48 px)** without looking generic or infringing.

**Recommended direction:** A single, geometric symbol that suggests **discovery + compliance** and (optionally) **crawl/scan**:

- **Option A – Magnifier + document/database:** Simple magnifying glass over a document or table icon (audit, inspection). Avoid clip-art style; use flat shapes and 1–2 colors so it scales and stays readable at 16 px.
- **Option B – Shield + check:** Shield with a check or tick (compliance, "approved"). Very clear for compliance tools; ensure the shape is original (no copy of known logos).
- **Option C – Abstract "C":** Stylized "C" for Compliance/Crawler, e.g. a C that doubles as a path or search arc. Works well as favicon and is easy to own.
- **Option D – Document + search:** Document/page with a small search or "scan" element (e.g. rays or a simple radar). Emphasizes "scanning documents/data."

**Copyright safety:** Design from scratch (no copying existing logos). Use simple shapes, limited palette (e.g. one brand color + dark gray/black, or two colors). No stock-art or third-party assets unless explicitly licensed for commercial use and logo use. Prefer **SVG** as the master so the same asset scales to favicon and report.

## Deliverables to produce (outside this repo):

| Asset             | Format         | Sizes / notes                                           |
| ---               | ---            | ---                                                     |
| Master logo       | SVG            | Single color or two-color; viewBox so it scales cleanly |
| Web logo          | PNG (from SVG) | e.g. 32px, 64px, 128px height                           |
| Favicon           | ICO or PNG     | 16x16, 32x32 (browsers accept PNG as favicon)           |
| Report (optional) | PNG            | 24x24 or 48x48 for embedding in Excel                   |

## Where to place files (after creation):

- Favicon: `api/static/favicon.ico` (and/or `api/static/favicon-32.png`).
- Web logo: `api/static/logo.svg`, `api/static/logo-64.png` (or similar).
- Report logo (optional): e.g. `api/static/logo-report-48.png` or under `report/` if you prefer to keep report assets separate.

---

## 2. Integration points (no design work, only integration)

Once the assets exist, wire them in as follows (no rule silencing or behavior change):

1. **Favicon**
   - In [api/templates/base.html](../api/templates/base.html) `<head>`: add

     `<link rel="icon" type="image/x-icon" href="/static/favicon.ico">`
     and optionally
     `<link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32.png">`
     so the browser and tabs show the icon.

1. **Web pages (optional)**
   - About: in [api/templates/about.html](../api/templates/about.html), optionally show the logo next to the app name (e.g. `<img src="/static/logo.svg" alt="" width="48" height="48">`).
   - Dashboard / Reports: same logo can be used in the header or "Application and report attribution" block in [api/templates/dashboard.html](../api/templates/dashboard.html) and [api/templates/reports.html](../api/templates/reports.html) if you want a consistent header.

1. **Excel report (optional, later)**
   - To use the logo in the spreadsheet: in [report/generator.py](../report/generator.py), when writing the "Report info" sheet, use openpyxl to insert an image (e.g. `logo-report-48.png`) at a fixed cell or above the Field/Value table. The generator would need the path to the image (e.g. from a package data dir or `api/static`). This is an optional enhancement so the same logo appears in the downloaded report.

1. **Heatmap**
   - Heatmap is a PNG with a text footer today; adding a small logo in a corner would require changes in [report/generator.py](../report/generator.py) `_create_heatmap` (e.g. paste a small image via matplotlib). Optional and can follow after the main logo is in place.

---

## 3. Application name change: options and availability

Current name: **python3-lgpd-crawler** (package and UI). Broader alternatives that still reflect "crawler + compliance/audit":

| Candidate name              | Pros                                              | Cons                                                                 | Availability note                                                                                                              |
| ---                         | ---                                               | ---                                                                  | ---                                                                                                                            |
| **compliance_crawler**      | Clear, broad (LGPD/GDPR/CCPA), describes behavior | Slightly generic; "crawler" can imply web crawler                    | Check PyPI, GitHub, and web for "Compliance Crawler" / "compliance_crawler" to avoid clashes with existing products or brands. |
| **pii_audit_crawler**       | Very descriptive (PII + audit + crawl)            | Longer; "PII" is US-centric                                          | Same checks.                                                                                                                   |
| **privacy_crawler**         | Short, privacy-focused                            | May sound like "crawling for privacy violations" in a negative sense | Check for existing "Privacy Crawler" tools.                                                                                    |
| **data_compliance_audit**   | Emphasizes audit and compliance                   | No "crawler"; less aligned with current naming                       | Check PyPI and GitHub.                                                                                                         |
| **lgpd_compliance_crawler** | Keeps LGPD, adds "compliance"                     | Still Brazil-heavy in the name                                       | Good if you want to keep LGPD prominent.                                                                                       |

**Recommendation:** **compliance_crawler** (or **python3-compliance-crawler** for the package) is a strong candidate: it's broader than "lgpd", keeps "crawler", and fits the current feature set. Before committing:

1. **PyPI:** Search for `compliance_crawler`, `compliance-crawler`, `python3-compliance-crawler` to see if the name is taken or very similar.
1. **Web / GitHub:** Search "Compliance Crawler" and "compliance_crawler" to avoid conflicting with an existing product or trademark.
1. If you keep **python3-lgpd-crawler** as the package name for backward compatibility, you can still use a **display name** like "Compliance Crawler" in the UI and docs (e.g. in [core/about.py](../core/about.py) `"name": "Compliance Crawler"` while keeping the package as `python3-lgpd-crawler`). That way installs and imports stay unchanged.

**If you rename the package** (e.g. to `python3-compliance-crawler`), the checklist is the same as in [docs/VERSIONING.md](VERSIONING.md): update `pyproject.toml` `name`, [core/about.py](../core/about.py) (name + fallback `version()` call), all references in docs (README, USAGE, man pages `lgpd_crawler.1` / `lgpd_crawler.5` and their filenames if you rename to `compliance_crawler.1` etc.), and any scripts or deploy configs that reference the package name.

---

## 4. What you can decide later

- **Logo:** Which concept (A–D) to use, exact colors, and whether to add the logo to the Excel "Report info" sheet and/or heatmap.
- **Name:** Whether to adopt **compliance_crawler** (or another candidate) after checking PyPI/GitHub/web; and whether to rename only the **display name** or the **package** as well.
- **Scope of integration:** Favicon + web only, or also report sheet and heatmap.

Mark to-dos in the table above and in [PLANS_TODO.md](PLANS_TODO.md) as done when each step is actually completed.
