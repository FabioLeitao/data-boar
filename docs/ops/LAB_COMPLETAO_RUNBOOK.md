# Lab “completão” vs CI / pytest

**Português (Brasil):** [LAB_COMPLETAO_RUNBOOK.pt_BR.md](LAB_COMPLETAO_RUNBOOK.pt_BR.md)

**Purpose:** Define what **completão** means in this project: **running the product** (CLI, API, web) on **lab hosts**, across **SSH**, with **documented** outcomes — not the same thing as **`pytest`** or **`.\scripts\check-all.ps1`** on the dev PC alone.

**New Cursor chat / zero context:** Use **[LAB_COMPLETAO_FRESH_AGENT_BRIEF.md](LAB_COMPLETAO_FRESH_AGENT_BRIEF.md)** — copy-paste prompts (**smoke-only** vs **extended**), optional checklists, follow-up blocks **B–E**, preconditions, and honest scope (what scripts run vs what needs operator config).

## Assistant and operator contract (Cursor)

- **Access:** The assistant runs **`ssh`**, scripts, and **`curl`** from the **Cursor integrated terminal** on the **operator’s Windows dev PC** — **same LAN and SSH config** as the operator’s shell (see **`homelab-ssh-via-terminal.mdc`**). Do **not** treat “assistant” as a separate network.
- **Default orchestration:** When the operator asks for **completão** or uses session keyword **`completao`**, the assistant should run **`.\scripts\lab-completao-orchestrate.ps1 -Privileged`** from the repo root unless the operator opts out. Logs: **`docs/private/homelab/reports/`**.
- **Privileged probes:** **`sudo -n`** in the smoke script requires **narrow sudoers** on each Linux host (template under gitignored **`LABOP_COMPLETÃO_SUDOERS*.md`**). **`sudo -v` in tmux** warms sudo for **that TTY**, not automatically for **non-interactive** `ssh host 'sudo …'` — for reliable **`-Privileged`** runs, align sudoers with the template.
- **On failure:** If **`sudo -n`** or SSH fails, the assistant **reminds** the operator to refresh sudoers / SSH agent / interactive sudo as needed, then **re-runs** the tests — see **`lab-completao-workflow.mdc`**.

- **Lab-as-test-datacenter scope:** For **completão**, the assistant **may** install **missing deps**, fix **app/compose ports**, add **narrow** **lab-op-to-lab-op** firewall or **VLAN** rules (via **`ufw`**, **`nftables`**, **UDM** scripts when configured), and tune **SELinux**/**AppArmor**/**fail2ban**/**sshguard**/**USBGuard**/**AIDE**/**auditd** (etc.) **only** with **least privilege** and **reversible** intent — full policy: **`lab-completao-workflow.mdc`**. Record what changed in **`docs/private/homelab/`**; never ship **secrets** or **LAN specifics** to **public** Git.

- **Wrappers + sudoers + no idle prompts:** Prefer **`lab-completao-orchestrate.ps1 -Privileged`** and related repo scripts (see **`LAB_OP_PRIVILEGED_COLLECTION.md`**, gitignored **`LABOP_COMPLETÃO_SUDOERS*.md`**) so remote hosts use **passwordless narrow sudo** for probes. **Do not** re-ask permission for the agreed SSH/**`-Privileged`** flow. **Protect** the **primary Windows dev PC** (**L-series** role, **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`**) and its **canonical** clone; **other** manifest hosts and **Docker** images may be **resynced** from **`origin`** / Hub for tests.

### Blast radius (contract — assistants must not confuse targets)

| Target | Git / repo policy | Rationale |
| ------ | ----------------- | --------- |
| **Primary Windows dev PC** (ThinkPad **L14**, Cursor workspace, **canonical** clone) | **Never** **`git reset --hard`**, **`git clean -fdx`**, **`clean-slate`**, or history rewrite on the **main** working tree. Use normal **`git pull` / merge / branch / stash**. | Continuity of evidence and history — **`PRIMARY_WINDOWS_WORKSTATION_PROTECTION.md`**. |
| **LAB-OP hosts** in **`lab-op-hosts.manifest.json`** (each **`repoPaths`** on SSH) | **Safe** to **`git fetch`**, **`git pull --ff-only`**, **`lab-op-git-align-main.ps1`**, **`lab-op-git-ensure-ref`**, **`-AlignLabClonesToLabGitRef`** — these scripts affect **only** those **remote** clones, **not** the L14 tree. | Disposable lab checkouts; align from GitHub **without** treating it like L14. |
| **Container images** (Docker / **Swarm** / **Podman** / **Kubernetes**) | **Re-pull** from **Docker Hub** (or configured registry); **`docker pull`**, stack/service update, prune — **normal** for lab. | Images are **reproducible** from registry — not the same blast radius as L14 Git. |

- **LAB-OP inventory map (hardware + software):** Before interpreting host-smoke results, assistants should **`read_file`** the private master chart **`docs/private/homelab/OPERATOR_SYSTEM_MAP.md`** and software matrix **`docs/private/homelab/LAB_SOFTWARE_INVENTORY.md`** when present (**`docs-private-workspace-context.mdc`**). **`lab-completao-orchestrate.ps1`** runs **`scripts/lab-completao-inventory-preflight.ps1`** first (default **15-day** freshness): if either file is missing or older than the threshold, it runs **`lab-op-sync-and-collect.ps1`** to refresh **`homelab-host-report`** telemetry under **`docs/private/homelab/reports/`** — then **merge** findings into the markdown inventories and bump an explicit **as-of** date (see *Inventory freshness* below). Opt out: **`-SkipInventoryPreflight`**; tune age: **`-InventoryMaxAgeDays N`**.

**Relationship:**

| Layer | What it is | Typical command |
| ----- | ---------- | ---------------- |
| **CI / unit & guards** | Reproducible, GitHub-hosted, no LAN secrets | `CI` workflow, `pytest` |
| **Dev PC gate** | Full local hook bundle + tests before merge | `.\scripts\check-all.ps1` |
| **Lab completão** | Product + runtime + LAN + optional DB stack + optional HTTP | `scripts/lab-completao-host-smoke.sh` per host; `scripts/lab-completao-orchestrate.ps1` from Windows |

**Canonical multi-host checklist** (manual steps A–M): [LAB_SMOKE_MULTI_HOST.md](LAB_SMOKE_MULTI_HOST.md).

## Inventory freshness (before / during completão)

**Why:** Hardware changes rarely; **software versions** (Python, Docker, distro packages) change often and affect decisions (e.g. container-only vs native **`uv`**, connector builds). Stale private inventories increase misinterpretation.

1. **Tracked automation:** **`scripts/lab-completao-inventory-preflight.ps1`** checks **`docs/private/homelab/LAB_SOFTWARE_INVENTORY.md`** and **`OPERATOR_SYSTEM_MAP.md`**. For each file it uses, in order: a line **`<!-- lab-op-inventory-as-of: YYYY-MM-DD -->`** or **`**Lab inventory as-of:** YYYY-MM-DD`** (or Portuguese *Inventário … as-of*), else **file LastWriteTime**.
2. **Default threshold:** **15 days** (`-MaxAgeDays` / **`-InventoryMaxAgeDays`** on the orchestrator). If **stale or missing**, **`lab-completao-orchestrate.ps1`** runs **`lab-op-sync-and-collect.ps1`** (same manifest) unless **`-SkipInventoryPreflight`**. Use **`-SkipGitPullOnInventoryRefresh`** on the orchestrator only if you want reports **without** **`git pull`** on lab clones.
3. **After telemetry:** **`lab-op-sync-and-collect`** does **not** rewrite the inventories — **update** the matrices from the latest `*_labop_sync_collect.log`, then set **as-of** near the top of each file so the next run’s age check is accurate.
4. **Manual preflight:** `.\scripts\lab-completao-inventory-preflight.ps1 -AutoRefresh` (same defaults).

## Target git ref for reproducible completão (LAB clones)

Host smoke runs `scripts/lab-completao-host-smoke.sh` from each `repoPaths` checkout. If those clones drift arbitrarily, a completão run is **not** comparable to CI, a release gate, or another session — you are exercising **whatever commit happens to be checked out**.

1. **Declare a ref:** optional root key **`completaoTargetRef`** in `docs/private/homelab/lab-op-hosts.manifest.json` (see `docs/private.example/homelab/lab-op-hosts.manifest.example.json`), and/or pass **`-LabGitRef`** to `lab-completao-orchestrate.ps1`. CLI **`-LabGitRef`** wins when non-empty; otherwise the manifest value is used.
2. **Check before smoke:** When a ref is set and **`-SkipLabGitRefCheck`** is **not** passed, the orchestrator runs **`scripts/lab-op-git-ensure-ref.ps1`** in **Check** mode (after inventory preflight, before SSH smoke). It `git fetch`es on each clone and **fails** if `HEAD` is not the resolved commit for that ref (`main` / `origin/main` → `origin/main` tip; release tags, branch names, and full SHAs supported). Logs: `docs/private/homelab/reports/lab_op_git_ensure_ref_*.log`.
3. **Release tags vs inventory refresh:** `lab-op-sync-and-collect.ps1` (run when inventory markdown is stale) performs **`git pull --ff-only`** on lab clones, which advances them to **latest `main`**. That can **break** a pin to **`vX.Y.Z`**. When testing a **tag**, pass **`-SkipGitPullOnInventoryRefresh`** on `lab-completao-orchestrate.ps1` so refresh does not move clones before **ensure-ref**; refresh private inventories manually if needed.
4. **Align / reset on LAB only:** **`lab-op-git-ensure-ref.ps1 -Mode Reset`**, **`lab-op-git-align-main.ps1`**, or **`lab-completao-orchestrate.ps1 -AlignLabClonesToLabGitRef`** with **`-LabGitRef`** (or manifest **`completaoTargetRef`**) apply **only** to **`repoPaths`** on **manifest SSH hosts** — **never** to the operator’s **canonical** clone on the **primary Windows dev PC (L14)**. Same risk class as **`lab-op-git-align-main.ps1`** on those remotes (drops local commits on **lab** clones / detached HEAD at tag).

## Capability coverage (documentation + code truth)

**Goal:** Learn **observed** behaviour vs **documented** intent — **English** docs and **code** are canonical ([docs/README.md](../README.md)). Completão should **exercise** (where lab resources allow): **remote storage** (NFS, SSHFS, SMB/CIFS — OS mounts and/or connector paths per [TECH_GUIDE.md](../TECH_GUIDE.md)); **databases** ([deploy/lab-smoke-stack](../deploy/lab-smoke-stack/), connectors per [ADDING_CONNECTORS.md](../ADDING_CONNECTORS.md)); **file types**, **extensions**, **hidden/dot** paths, **archives**; **local vs remote** targets; **LGPD-oriented discoverables** as **detection language** ([COMPLIANCE_AND_LEGAL.md](../COMPLIANCE_AND_LEGAL.md) — not legal advice); **ML/DL sensitivity** ([SENSITIVITY_DETECTION.md](../SENSITIVITY_DETECTION.md), [TESTING.md](../TESTING.md)); **reports** and **dashboard** flows; **POC** paths — maturity questionnaire ([SMOKE_MATURITY_ASSESSMENT_POC.md](SMOKE_MATURITY_ASSESSMENT_POC.md)), **WebAuthn/FIDO2** JSON RP ([SMOKE_WEBAUTHN_JSON.md](SMOKE_WEBAUTHN_JSON.md), [SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.md](SECURE_DASHBOARD_AUTH_AND_HTTPS_HOWTO.md), [ADR 0033](../adr/0033-webauthn-open-relying-party-json-endpoints.md)). **Secure-by-design** claims must align with [SECURITY.md](../SECURITY.md) and **what actually ran**. Record **pass / gap / drift** in **private** session notes (`docs/private/homelab/`) — **policy:** **`.cursor/rules/lab-completao-workflow.mdc`** (capability matrix section).

## Scripts (tracked)

1. **`scripts/lab-completao-host-smoke.sh`** (run **on each Linux lab host**, from repo root): `uv`, `docker` / `podman`, `deploy/lab-smoke-stack` compose `ps` if present, optional **`LAB_COMPLETAO_HEALTH_URL`** or **`--health-url`** for `/health`, quick **`import core.engine`** unless **`--skip-engine-import`** (or **`LAB_COMPLETAO_SKIP_ENGINE_IMPORT=1`**) — see **Container-only lab hosts** below. **`--privileged`**: read-only snapshots via **`sudo -n`** (iptables/nft/ufw/fail2ban-related) — skips if sudo cannot run non-interactively.

2. **`scripts/lab-completao-orchestrate.ps1`** (run **on the Windows dev PC**): reads **`docs/private/homelab/lab-op-hosts.manifest.json`** (same idea as **`lab-op-sync-and-collect.ps1`**); optional root **`completaoTargetRef`** or CLI **`-LabGitRef`** triggers **`lab-op-git-ensure-ref.ps1`** before smoke unless **`-SkipLabGitRefCheck`**; SSH to each **`sshHost`**, runs the bash script for each **`repoPaths`** entry; optional per-host **`completaoHealthUrl`**: after SSH smoke, **`Invoke-WebRequest`** from the dev PC (LAN client view); optional **`completaoEngineMode`:** **`container`** or **`completaoSkipEngineImport`:** **`true`** passes **`--skip-engine-import`** to the host smoke (Docker Swarm / Podman-only hosts with **no** bare-metal **`uv`**); writes **`docs/private/homelab/reports/completao_<timestamp>_allhosts.log`** plus per-host `*_completao_host_smoke.log`.

3. **Passwordless sudo (narrow)** — same discipline as **`homelab-host-report.sh`**: template under **gitignored** **`docs/private/homelab/LABOP_COMPLETÃO_SUDOERS.pt_BR.md`**. Do **not** commit real sudoers content to GitHub.

4. **Session log / lessons template** — **`docs/private/homelab/COMPLETAO_SESSION_TEMPLATE.pt_BR.md`** (gitignored private tree): date, host, pass/fail, value, lessons learned. Filled examples stay under **`docs/private/homelab/`** as **`COMPLETAO_SESSION_YYYY-MM-DD.md`** (operator-only; never public GitHub).

5. **`scripts/lab-op-repo-status.ps1`** (Windows): **`git fetch`** + **`git status -sb`** on each **`repoPaths`** (no reset). Optional **`-PullFfOnly`** for **`git pull --ff-only`** when the clone is strictly behind. **Start here** when orchestrate reports **`MISSING_SCRIPT`** — usually the clone is older than **`main`**.

6. **`scripts/lab-op-git-ensure-ref.ps1`** (Windows): for each host, **`git fetch`** on each **`repoPaths`** clone, then **Check** (fail if `HEAD` ≠ resolved ref) or **Reset** (destructive checkout/reset to match the ref). Used automatically by **`lab-completao-orchestrate.ps1`** when **`completaoTargetRef`** / **`-LabGitRef`** is set — see *Target git ref for reproducible completão* above.

7. **`scripts/lab-op-git-align-main.ps1`** (Windows): for each host in the same manifest, **`git fetch`** + **`git reset --hard origin/main`** on each **`repoPaths`** entry. **Destructive** (drops local commits on the clone); use when LAB-OP trees must match GitHub **`main`** and you accept losing local-only commits on those clones. For non-**`main`** refs (e.g. release tags), prefer **`lab-op-git-ensure-ref.ps1 -Mode Reset`**.

8. **Ansible (optional):** **`ops/automation/ansible/playbooks/lab-op-data-boar-git-sync.yml`** — alignment via group **`lab_op_data_boar`** in a local inventory (see **`inventory.example.ini`**). Reproducible when Ansible is already part of your operator workflow.

9. **Filesystem templates (tracked, copy to private or `~` on Linux):** **`docs/private.example/homelab/config.lab-fs-varlog.example.yaml`**, **`config.lab-fs-home-leitao.example.yaml`** — run **`main.py`** **on the same host** as the paths (SSH + `export PATH=$HOME/.local/bin:$PATH`; **`mkdir -p`** report/sqlite dirs first). **`/var/log`** may emit **`permission_denied`** for non-root users on some files — expected.

10. **MongoDB in completão:** connector **`driver: mongodb`**; install **`pymongo`** with **`uv sync --extra nosql`**. Bring up the optional stack: **`deploy/lab-smoke-stack`**: **`docker compose -f docker-compose.yml -f docker-compose.mongo.yml up -d`** (published port **27018** by default). If Mongo is down, the target fails as **unreachable**, not **unsupported**.

## Container-only lab hosts (Docker Swarm, Podman stack, no bare-metal `uv`)

Some lab machines are **orchestrator** or **policy** roles: the operator runs Data Boar **only** via **Docker** / **Podman** / **Docker Swarm** (stack or service), and **does not** rely on **`uv`** on the host for SSH-driven checks. That is a **valid** completão posture when recorded in the private manifest — assistants should **not** treat “`uv` not in PATH” on those hosts as a defect to “fix” by forcing a host Python env.

1. In **`docs/private/homelab/lab-op-hosts.manifest.json`**, set **`completaoEngineMode`** to **`container`** **or** **`completaoSkipEngineImport`** to **`true`** for that **`sshHost`**. **`lab-completao-orchestrate.ps1`** then passes **`--skip-engine-import`**; the smoke logs an explicit **skipped** line for **`import core.engine`** instead of implying failure.
2. **Success criteria** on those hosts: container runtime CLI healthy, optional **`deploy/lab-smoke-stack`** **`compose ps`** when compose is used there, and/or **`completaoHealthUrl`** (e.g. published **`8088`**) returning **200** from the dev PC.
3. **Filesystem / CLI scans** against paths on that host still need **some** runtime (bind-mounted **`uv run`** inside a container, or another documented path). The host smoke **does not** replace that — note in private session files which approach you used.

See **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`** for optional fields.

## Recommended slice order (one host at a time)

1. **Target ref (recommended for comparable runs):** set **`completaoTargetRef`** (e.g. **`origin/main`** or **`vX.Y.Z`**) and/or **`-LabGitRef`** on **`lab-completao-orchestrate.ps1`**; use **`-SkipGitPullOnInventoryRefresh`** when pinning a **tag**. Optional: **`lab-op-repo-status.ps1`** (inspect) then **`lab-op-git-align-main.ps1`**, **`lab-op-git-ensure-ref.ps1`**, or **`git pull --ff-only`** when you accept **destructive** reset or fast-forward on LAB clones.
2. **Host smoke:** **`lab-completao-orchestrate.ps1`** (or **`lab-completao-host-smoke.sh`** over SSH) until **`MISSING_SCRIPT`** is gone and, for **native** hosts, **`import core.engine`** succeeds. **Container-only** hosts (manifest **`completaoEngineMode`:** **`container`** or **`completaoSkipEngineImport`:** **`true`**) **skip** bare-metal import; validate **Docker/Podman/Swarm** + **`completaoHealthUrl`** instead.
3. **FS `/var/log`:** copy **`config.lab-fs-varlog.example.yaml`**, run **`uv run python main.py --config …`** **on that Linux host** (not from Windows unless paths are mounted).
4. **FS home tree:** same with **`config.lab-fs-home-leitao.example.yaml`** (adjust username if not **`leitao`**).
5. **CLI completão** from the dev PC with a **private** YAML (DBs on a hub + synthetic FS under the repo) — see **`docs/ops/LAB_EXTERNAL_CONNECTIVITY_EVAL.md`** and private **`config.complete-eval.yaml`** pattern.
6. **API / web:** start **`main.py --web`** on a host; **`curl http://<host>:8088/health`** from another LAN machine; then browser. Add **`completaoHealthUrl`** to the manifest for orchestrate to probe from Windows.

## Automation boundary vs assistant-led remediation

- **Built-in scripts** (`lab-completao-orchestrate`, host-smoke) **do not** by themselves open **firewalls** or relax **LSM**/**integrity** tools — they **probe** and **log**.
- When the operator asks for **completão** and wants tests **unblocked**, the assistant **may apply** **narrow**, **lab-op-scoped**, **least-privilege** fixes (packages, ports, **`ufw`**/**nft**, UniFi via **`udm.ps1`** when keys exist, container paths, NFS/SMB/SSHFS mounts per product support) per **`lab-completao-workflow.mdc`**. **Escalate** to the operator before **broad** or **irreversible** hardening changes.
- **Production readiness** stays **iterative**: repeat completão, file issues, patch code/docs, re-run.

## Automation reuse and documented learnings

- **Encode repeat work:** When a completão step is **repeatable**, add or extend **`scripts/`**, **Ansible** under **`ops/automation/ansible/`**, or **manifest** fields — hub: **[TOKEN_AWARE_SCRIPTS_HUB.md](TOKEN_AWARE_SCRIPTS_HUB.md)**; policy: **`lab-completao-workflow.mdc`** (*Automation reuse + documented learnings*).
- **Capture signals in private session notes** (`docs/private/homelab/`, template **`COMPLETAO_SESSION_TEMPLATE.pt_BR.md`**): **timeouts**, **wall-clock** duration, **unexpected slowness**, **FP/FN** vs **known synthetic** ground truth (report vs expected), **confidence** on **real** paths (e.g. system log trees, home-directory samples), **latency** over **public APIs** / **SSH** / **low-resource** lab hosts vs faster machines, and any **default**/**doc** mismatch. These feed **`PLANS_TODO.md`** / **issues** — **no** raw PII in public Git.

## Quick start

1. For hosts where you run the **product on bare metal**, ensure the repo clone and **`uv`** (often **`~/.local/bin/uv`** — **`lab-completao-host-smoke.sh`** prepends that to **`PATH`**); run **`uv sync`** and **`uv sync --extra nosql`** if Mongo targets are in your YAML (and [TECH_GUIDE.md](../TECH_GUIDE.md) extras for compressed/shares as needed). For **container-only** hosts (Swarm manager, Podman-only, etc.), set **`completaoEngineMode`:** **`container`** (or **`completaoSkipEngineImport`:** **`true`**) and rely on **HTTP** / compose / stack checks — do **not** assume **`uv`** on the host.
2. Optional manifest fields: **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`** (root **`completaoTargetRef`** documented in **`docs/private.example/homelab/README.md`**; per-host **`completaoHealthUrl`**, **`completaoEngineMode`**, **`completaoSkipEngineImport`**).
3. From repo root on Windows: **`.\scripts\lab-completao-orchestrate.ps1 -Privileged`** (assistant-led completão default; omit **`-Privileged`** only if you must avoid privileged probes).
4. Append lessons to the private template (**timeouts**, **FP/FN**, **latency**, **confidence**); link findings to **`PLANS_TODO.md`** / issues when product gaps appear.
