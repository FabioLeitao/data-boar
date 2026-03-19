# Home lab: deployment checks and target validation (manual playbook)

**Português (Brasil):** [HOMELAB_VALIDATION.pt_BR.md](HOMELAB_VALIDATION.pt_BR.md)

**Purpose:** Run **concrete checks** on a **second machine** (VM or container host) to prove **deployability**, **smoke behaviour**, and **connector coverage** using **synthetic** and optionally **small real** datasets—without relying on CI or the dev laptop alone.

**Not legal advice.** For **real** personal data, use **lawful basis**, **minimisation**, and **read-only** technical accounts; prefer **synthetic** or **public sample** data when unsure.

**Related:** [deploy/DEPLOY.md](deploy/DEPLOY.md) · [SONARQUBE_HOME_LAB.md](SONARQUBE_HOME_LAB.md) (optional quality server) · [OPERATOR_IT_REQUIREMENTS.md](OPERATOR_IT_REQUIREMENTS.md) · [TESTING.md](TESTING.md) · [SECURITY.md](../SECURITY.md)

---

## 0. Principles

1. **Automate locally first (any machine):** from repo root, `.\scripts\check-all.ps1` (Windows) or equivalent pre-commit + `uv run pytest -v -W error` (Linux/macOS). Fix reds before spending time on lab networking.
1. **Lab is for integration:** OS paths, Docker volumes, real DB ports, firewall, and “does this config actually run here?”
1. **Synthetic by default:** hand-made `.txt` / `.csv` with **fake** CPF/email patterns (see project tests for valid-format examples—do not use real people’s data).
1. **Real data only when allowed:** copies of non-production DBs, anonymised extracts, or documents you own/have permission to scan.

---

## 1. Lab baseline checklist (copy/paste)

| Step | Action | Pass criteria |
| ---- | ------ | ------------- |
| 1.1 | Clone repo on lab (or `git pull`); `uv sync` | Dependencies install |
| 1.2 | `uv run pytest -v -W error` or project check script | All tests green |
| 1.3 | `docker build -t data_boar:lab .` | Build completes |
| 1.4 | Create `./data/config.yaml` from [deploy/config.example.yaml](../deploy/config.example.yaml) | File valid YAML |
| 1.5 | `docker run --rm -p 8088:8088 -v "$(pwd)/data:/data" -e CONFIG_PATH=/data/config.yaml data_boar:lab` | Dashboard loads at `:8088`, `/health` OK |
| 1.6 | **Start scan** (dashboard or `POST /scan`) with `targets: []` | Completes idle run; no crash |

---

## 2. Synthetic filesystem target (fastest real connector test)

1. On the lab host, create a directory, e.g. `~/lab-scan/fs-sample/`.
1. Add files:
   - `notes.txt` — a line with a **synthetic** CPF in valid format (e.g. use a known test pattern from `tests/test_audit.py` commentary—**not** a real person).
   - `sheet.csv` — header `email` and one row with `test@example.invalid`.
1. In `config.yaml`, set:

```yaml
targets:
  - name: lab-fs
    type: filesystem
    path: /data/fs-sample   # inside container: mount host dir to /data/fs-sample
    recursive: false
file_scan:
  extensions: [.txt, .csv]
  recursive: false
  scan_sqlite_as_db: false
  sample_limit: 5
```

1. Mount: `-v ~/lab-scan/fs-sample:/data/fs-sample` (adjust host path).
1. Run CLI one-shot or dashboard scan.
1. **Pass:** findings appear in SQLite/report; filesystem findings &gt; 0 for obvious patterns.

**Optional:** enable `use_content_type: true` or dashboard **content-type** checkbox; add a file `disguised.txt` whose bytes start with `%PDF-1.` to confirm magic-byte path (see [USAGE.md](USAGE.md)).

---

## 3. SQLite as a “database” file (single file, no server)

1. Create or copy a small `.db` with one table and a few text columns (or use Python `sqlite3` once to insert synthetic rows).
1. Target type **filesystem** with `scan_sqlite_as_db: true` **or** a **database** target pointing at SQLite connection string—follow [USAGE.md](USAGE.md) for your chosen shape.
1. **Pass:** session completes; database findings or filesystem path shows SQLite was read.

---

## 4. PostgreSQL or MySQL/MariaDB in Docker (lab SQL)

1. Start a throwaway DB container on the lab (same Docker network as the app, or publish port to host).

```bash
# Example: Postgres
docker network create lab-net
docker run -d --name lab-pg --network lab-net -e POSTGRES_PASSWORD=labpass -e POSTGRES_DB=labdb postgres:16-alpine
```

1. Create a table `customers (id serial, full_name text, doc_id text)`; insert **synthetic** rows.
1. Add a **database** target in `config.yaml` with host `lab-pg` (if app container on `lab-net`) or `host.docker.internal` / LAN IP from host networking docs.
1. Use **read-only** user if possible.
1. **Pass:** scan connects; findings or empty result without connection errors; check `scan_failures` in session.

**MySQL/MariaDB:** same idea; install connector deps per [TECH_GUIDE.md](TECH_GUIDE.md).

---

## 5. NoSQL (optional extras)

- **MongoDB:** requires `uv sync --extra nosql` (or equivalent); small collection with synthetic documents.
- **Redis:** string values with synthetic emails; respect memory and TTL in lab.

**Pass:** connector runs; document any `ModuleNotFoundError` as “install extra” in your runbook.

---

## 6. REST API target (optional)

- Point at a **mock** or trivial JSON API in the lab (e.g. small Flask container returning static JSON with synthetic fields).
- **Pass:** API connector completes; findings or logged skip reasons are understandable.

---

## 7. Compressed archives (`scan_compressed`)

1. Add a `.zip` containing one `.txt` with synthetic PII pattern.
1. Set `file_scan.scan_compressed: true` or CLI `--scan-compressed` / dashboard checkbox.
1. Install **compressed** extra if using `.7z` (`uv sync --extra compressed`).
1. **Pass:** inner file contributes findings.

---

## 8. Licensing smoke (optional, enforced mode)

1. With `licensing.mode: enforced` and **no** valid `.lic`, expect CLI/API **block** (see [LICENSING_SPEC.md](LICENSING_SPEC.md)).
1. Return to `open` for general lab testing unless you are explicitly validating commercial packaging.

---

## 9. SonarQube (optional)

If you run a lab SonarQube server, follow [SONARQUBE_HOME_LAB.md](SONARQUBE_HOME_LAB.md). Validation there is **code quality**, not data connectivity.

---

## 10. Record results (lightweight)

Keep a **dated note** (e.g. in `docs/private/` gitignored or a personal wiki): date, image tag, targets tried, pass/fail, and **one** lesson (e.g. “Postgres needed `host` = service name on lab-net”). Updates **PLANS_TODO** only when you change supported behaviour or find a doc gap worth fixing in-repo.

---

## 11. When you are “done” with a lab pass

- Image builds; default **open** licensing; **at least one** filesystem synthetic run; **optional** one SQL container run.
- **Production** still needs your org’s backup, secrets, TLS, rate limits, and legal review—this playbook is **technical confidence**, not a prod sign-off.

---

## See also

- [TOKEN_AWARE_USAGE.md](plans/TOKEN_AWARE_USAGE.md) — after lab validation, return to one-row-per-session feature work ([PLANS_TODO.md](plans/PLANS_TODO.md)).
- [CODE_PROTECTION_OPERATOR_PLAYBOOK.md](CODE_PROTECTION_OPERATOR_PLAYBOOK.md) — Priority band A (deps, Scout, Hub) before heavy feature bursts when urgent.
