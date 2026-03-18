# Portfolio and evidence sources (thesis, pitch, CV narrative)

**Purpose:** Single place to list **where** to get (or add) evidence for thesis, compliance narrative, and pitch. Keeps sessions token-efficient: open this file + one source at a time. See [TOKEN_AWARE_USAGE.md](TOKEN_AWARE_USAGE.md) §3 for how this ties into plans.

**Policy:** Public URLs and repo paths only. No sensitive or private content here; private docs stay in `docs/private/` (git-ignored) and are referenced by filename.

---

## 1. Docker images and Dockerfiles

| Image | Docker Hub | GitHub / Dockerfile | Notes (fetched or from you) |
| ----- | ---------- | ------------------- | --------------------------- |
| **data_boar** | [hub.docker.com/r/fabioleitao/data_boar](https://hub.docker.com/r/fabioleitao/data_boar) | This repo: **[Dockerfile](https://github.com/FabioLeitao/data-boar/blob/main/Dockerfile)** (multi-stage, python:3.12-slim, builder + runtime). Tags e.g. `1.6.0`, `latest`. | Short description on Hub; full description with quick start and link to GitHub. Size ~186 MB (1.6.0). |
| **wildfly_t1r** | [hub.docker.com/r/fabioleitao/wildfly_t1r](https://hub.docker.com/r/fabioleitao/wildfly_t1r) | **[FabioLeitao/wf_t1r](https://github.com/FabioLeitao/wf_t1r)** (Shell). Dockerfiles live in that repo if you want to paste or link them here later. | Archived on Hub. Tag e.g. `et-ojdk8-a_w26.1.1-final`. Eclipse Temurin + Wildfly; Ubuntu/Alpine; OpenJDK 8/11/17/19; Oracle JDBC. |
| **uptk** | [hub.docker.com/r/fabioleitao/uptk](https://hub.docker.com/r/fabioleitao/uptk) | No overview on Hub. If you have a repo or Dockerfile for Uptime Kuma, add the link here. | Tag `0.1`, ~3.1 MB. You keep upgrading on the actual server. |

**Optional:** You can add a short `docs/private/Dockerfiles_used.md` (or paste Dockerfiles there) for wf_t1r/uptk so thesis or narrative can cite “Dockerfiles created and used” without opening GitHub in every session.

---

## 2. GitHub repositories (public)

| Repo | Description | Use in narrative |
| ---- | ----------- | ----------------- |
| **FabioLeitao/data-boar** | This project (Data Boar). | Main compliance/LGPD artifact; Dockerfile in repo root. |
| **FabioLeitao/python3-lgpd-crawler** | Legacy/history-only (no push). | Historical reference for naming and evolution. |
| **FabioLeitao/wf_t1r** | Container Eclipse Temurin + Wildfly tunado para testes. | Java/infra/SRE; multi-version JDK/Wildfly. |
| **FabioLeitao/python3-qrcodegenerator** | QRCode images from file list (labels). | Utility/automation. |
| **FabioLeitao/auto_uploader** | Bash automação de transferência de arquivos. | Automation/SRE. |
| **bash_busca_vm_proxmox**, **bash_cups_control**, **bash_jboss_monitor** | PRTG/Proxmox/CUPS/jBoss scripts. | Monitoring, infra, ops. |

**Profile:** [github.com/FabioLeitao](https://github.com/FabioLeitao) – 26 public repos; location Niterói; recent activity data-boar.

---

## 3. Certifications and community (for thesis/CV/pitch)

Add only what you are comfortable making reference to in docs; keep wording factual.

| Item | How to use |
| ---- | ---------- |
| **LPIC-1 (101)** | Certification; supports Linux/systems and infra narrative in thesis and bio. |
| **PUC-RS – IA e IoT** | Recent certification (AI and IoT); supports ML/DL and “diverse data sources” narrative; PUC-RS adds academic weight for thesis and advisor outreach. **File:** `docs/private/Certificado_IA_IOT_PucRS_Fabio.pdf`. Curso de Extensão "Internet das Coisas, IA e a Revolução Conectada" (Escola de Negócios PUC-RS, 10 h/aula, Porto Alegre 20/02/2026). Conteúdo: arquitetura IoT, 5G/6G, LGPD/dados, IA, transformação digital, cidades inteligentes. Validação: educon.pucrs.br/validarcertificado código 256371-904-1. |
| **Ubuntu tester / collaborator** | Community contribution; supports quality, testing, and open-source narrative. |
| **Launchpad (Canonical/Ubuntu)** | **[launchpad.net/~fabio-tleitao](https://launchpad.net/~fabio-tleitao)** (PresuntoRJ). Member since 2005-10-19; signed Ubuntu Code of Conduct. Teams: Ubuntu Brasil, Ubuntu Brazilian Security Team, Ubuntu Server Team, Launchpad Translators, Ubuntu on Rails. IRC: PresuntoRJ (Freenode #ubuntu, #ubuntu-br, etc.). **Location:** Niterói - RJ (Launchpad may still show Rio de Janeiro; that is stale). Languages EN, PT. Use for Ubuntu/community narrative and credibility. |
| **RCDD BICSI** (former; renewal lapsed – expensive renewal, limited value in BR at the time; may renew someday) | Registered Communications Distribution Designer ([BICSI](https://www.bicsi.org/)). **File:** `docs/private/titulo-rcdd.jpeg`. Supports telecom/infra/cabling narrative; strong for CV and thesis background. |
| **DataPrev – Analista de Cibersegurança** | Passed the selective exam for Cybersecurity analyst at DataPrev; **6th place overall**. Awaiting allocation (call from DataPrev). When you have evidence of classification (e.g. result notice, ranking), add to `docs/private/` (e.g. `DataPrev_exame_classificacao.pdf` or screenshot); we’ll reference by filename for CV and narrative. |
| **Other communities / forums** | TrueNAS, FreeBSD (e.g. FUG-BR), Void Linux, Zorin Pro (paying user), etc. All count: they support infra, storage, BSD, minimal Linux, and ecosystem engagement. Add links or one-liners in §3 or here when you want them cited (no need to paste forum content). |
| *(Optional)* Other certs (e.g. LPIC-2, cloud, security) | Add a row here when you want them cited. |
| *(Optional)* Talks, blog, articles | Add URLs or one-liners here when you want them in the narrative. |

**Learning platforms (Udemy, Alura, etc.):** Certifications and courses from CV are listed in §3.2. We don’t have your full course/cert list from CV or LinkedIn here. For in-progress or paid-not-started, add or update `docs/private/Learning_and_certs.md` for prioritisation.

---

### 3.1 Certifications and learning – sequenced to-do (production + academic)

Use this when you (re)find **paid but incomplete** certs or want to pick **low-effort, high-gain** certs. Store your list in `docs/private/Learning_and_certs.md` (or similar); this section stays as the sequenced checklist.

| Order | To-do | Why (production / academic) |
| ----- | ----- | ---------------------------- |
| 1 | **List paid / incomplete certs** (platform, course name, link if any). | So we don’t lose track; prioritise by effort vs gain. |
| 2 | **Prioritise 1–2** as “low effort, high gain” for this cycle. | Focus beats scattering; one cert finished > three half-done. |
| 3 | **Complete the chosen cert(s)** and save proof in `docs/private/` (PDF/screenshot). | Adds to §3 table and CV/thesis narrative. |
| 4 | **Update this file** (§3 table) and optional checklist in PLANS_TODO or TOKEN_AWARE. | Keeps portfolio and plans in sync. |

**Low-effort, high-gain (suggestions):** Prefer certs that support **both** production readiness and academic narrative: e.g. **LGPD / privacy / DPO awareness** (short courses, many on Udemy/Alura), **ISO 27001/27701 awareness**, **cloud fundamentals** (AWS/GCP/Azure free or low-cost), **security basics** (e.g. CompTIA Security+ prep, or platform-specific). Avoid long, expensive ones unless they’re already paid and near completion. When in doubt, finish one you’ve already paid for before buying new.

---

### 3.2 Certifications and courses (from CV – LEITAO_Candidates_Resume_BR.pdf, p.2)

Source: **`docs/private/LEITAO_Candidates_Resume_BR.pdf`**, section "CERTIFICAÇÕES E CURSOS COMPLEMENTARES" (second page). Use for narrative, prioritisation, and §3.1 sequenced to-do.

| Platform / issuer | Course / certification | Year |
| ------------------ | ---------------------- | ---- |
| PUCRS | Curso de Extensão IOT e IA - Revolução Conectada | 2026 |
| IBM | Cybersecurity Fundamentals; On the Defense (MDL-407); On the Offense (MDL-405); Introduction to Cybersecurity (MDL-403) | 2024 |
| Certiprof | Cyber Security Foundation Professional Certificate (CSFPC) | 2023 |
| IBM | Protect from Ransomware | 2023 |
| Qude / DevOps Institute | SRE Fundamentals; SRE Practitioner | 2022 |
| SOLAS | ISPS Code | 2025 |
| Udemy | Ethical Hacking; Rust Completo; Python 3; Selenium WebDriver; Terraform with Ansible; Odin Bootcamp; Ansible SysAdmin | 2023–2025 |
| Alura | Go (linguagem, OO, app web); Go e Gin API rest; AZ-900 Azure Fundamentals; SRE confiabilidade | 2023–2024 |
| LPI | LPIC-1 Exam 101 | 2008 |
| Microsoft | Microsoft Certified Professional (70-271) | 2000 |

*For in-progress or paid-not-started, add or update `docs/private/Learning_and_certs.md`.*

---

### 3.3 Education, monitoring, and technical background (for narrative / CV)

- **UFRJ (student):** Studied at UFRJ (taught by their professors). Worked at the **LCI Lab** during student years. **Monitored** students (helping the teacher and students who needed help with course content, classes, and IT lab).
- **UESA (Telecommunications):** While studying Telecommunications at UESA, **monitored and assisted** the Physics class.
- **Systems and platforms (early adoption and breadth):** Linux since kernel **0.96** (before Slackware), Novell NetWare 3 and later 4 (network servers), DOS 3.3 onward, Windows 3.1 onward, OS/2 Warp 3 and 4, OpenSolaris, AIX (RISC/6000 workstations), HP-UX, etc. Supports narrative of long-standing systems and infra experience across many OSes and eras.
- **Monitoring and custom sensors:** Hand-crafted custom sensors for **PRTG** (usually Bash), **Nagios** (usually Bash), and **Zabbix**. Fits SRE/observability narrative (CV already mentions PRTG, Zabbix, Uptime Kuma, etc.).
- **Security, backup, and infrastructure stack:** Deployed **Wazuh**; Symantec EPP and AV, **Backup Exec**; IBM Tivoli (including BladeCenter H cluster running **VMware**, 2010s). Avid **Proxmox** administrator; **Synology** solutions. **TrueNAS** admin (both BSD- and Linux-based). **UniFi** networking (dual WAN/load-balanced UniFi DM at home; also administered at office). **pfSense** at home and office: Suricata or Snort IDS/IPS, DNS/regional/proxy filtering and rules via pfSense packages. **Cisco ASA**, **Fortinet FortiGate**. **MISP** deployed for threat intelligence gathering (previous job). **Asterisk** SoftPBX deployment (VoIP and POTS lines). Supports security, hardening, threat intel, and compliance narrative (Data Boar, LGPD, cibersegurança).
- **Languages (work and personal projects, including before GitHub and similar):** Pascal (Turbo, Borland, Delphi, Lazarus, FPC, etc.), C/C++, and some Visual Basic. **Scripting and current development:** Bash, Python, Expect; plenty of .bat, .cmd, VBS, and .ps1 (PowerShell) for Windows/systems automation; and the stack behind current work (e.g. Data Boar, Python, Go, Rust from CV). Supports narrative of long-standing programming practice, breadth of stacks, and evolution from desktop/legacy to modern tooling.

*No artifact to “fetch”; reference in bio and “Formação e experiência” when drafting thesis or pitch.*

---

## 4. Private docs (do not commit content)

Stored in **`docs/private/`** (git-ignored). Reference by **filename** only in plans.

### 4.1 PUC-Rio program (enrolled) – Compliance de Cibersegurança

Fetched from [PUC-Rio Digital – Compliance de Cibersegurança](https://especializacao.ccec.puc-rio.br/especializacao/compliance-de-ciberseguranca). Use for lato sensu thesis plan alignment (objectives, structure, TCC).

| Item | Detail |
| ----- | ------ |
| **Name** | Pós-Graduação em Compliance de Cibersegurança (Especialização Lato Sensu) |
| **Institution** | PUC-Rio (CCEC – Coordenação Central de Educação Continuada), formato PUC-Rio Digital |
| **Duration** | 12 meses (ou 15 com Sprint de Aperfeiçoamento "Do Zero ao Código") |
| **Carga horária** | 480 horas |
| **Format** | 100% online; aulas gravadas + encontros ao vivo; certificação Lato Sensu PUC-Rio |
| **Structure** | Sprints a cada 3 meses (3 disciplinas + 1 MVP por sprint). **Blocos:** (1) Segurança Ofensiva: Ameaças, Ataques e Crimes; (2) Segurança Defensiva: Gestão de Controles, Riscos e Continuidade de Negócio; (3) Gestão de Incidentes e Privacidade de Dados + IA; (4) Governança e Forense. |
| **LGPD / privacidade** | Disciplina **"Gestão da Privacidade de Dados Pessoais (LGPD e RIPD)"** (30h) – princípios de privacidade, LGPD, GDPR, ferramentas de conformidade. Professores incluem Caitlin Mulholland (ex-CNPD, Diretora Dept. Direito PUC-Rio), Anderson da Silva. |
| **Relevance to Data Boar / thesis** | Direct fit: compliance digital, privacidade de dados, governança de dados com cibersegurança, gestão de riscos. Thesis can frame Data Boar as artefato de apoio à conformidade e evidências (LGPD, ISO 27xxx) dentro deste programa. |

Optional: add official "Guia do Curso", ementa completa, or TCC norms to `docs/private/` when you have them.

---

- CV, TCC, LinkedIn: see [TOKEN_AWARE_USAGE.md](TOKEN_AWARE_USAGE.md) §3.
- **From Docker hub list of repositories.md** – authoritative list of Docker Hub repos (data_boar, wildfly_t1r, uptk).
- **Certificates:** **PUC-RS IA e IoT:** `Certificado_IA_IOT_PucRS_Fabio.pdf`. **RCDD:** `titulo-rcdd.jpeg`. Reference by filename in §3. |
- **PUC-Rio (recently enrolled):** Program fetched and summarised in §4.1 (Compliance de Cibersegurança). Optional: add TCC norms or enrollment confirmation (PDF/screenshot) to `docs/private/` (e.g. `PUC_Rio_program_requirements.pdf`). We’ll use it for the lato sensu thesis plan (objectives, structure, deadlines). |
- **Learning and certs (optional):** `Learning_and_certs.md` – list completed, in progress, and paid-not-started courses/certs (Udemy, Alura, etc.). Use for prioritisation and §3.1 sequenced to-do.
- Any new PDF/MD you add: add the filename to TOKEN_AWARE_USAGE §3 or to this section.

---

## 5. What to get next – recommendations

Use this when you can "try to get" something and want to prioritise. Ordered by **impact on the plans** and **realistic to obtain**.

| Priority | What to get | Why it helps | Where to put it |
| -------- | ----------- | ------------ | ----------------- |
| **1** | **Program / course requirements** (lato sensu) | If you already have a program or course: official "estrutura do TCC", "critérios de avaliação", or "normas da ABNT" (1–3 pages). | `docs/private/` (e.g. `program_tcc_requirements.pdf`). Then we align thesis outline (PLAN_LATO_SENSU §1.2, §5.2) to it. |
| **2** | **1–2 redacted report excerpts** (Data Boar) | One inventory sheet and one heatmap/summary (fake or anonymised data) as PDF or screenshots. | `docs/private/` (e.g. `sample_report_inventory.pdf`, `sample_heatmap.png`). Thesis "case study" and "outputs" (PLAN_LATO_SENSU §4.2) can reference them. |
| **3** | **Architecture diagram export** | TOPOLOGY.md is textual. One visual (Mermaid → PNG/SVG, or draw.io) "high-level components + scan pipeline" for the thesis. | `docs/` (e.g. `topology-diagram.png`) or thesis folder. PLAN_LATO_SENSU §3.1 needs "1–2 architecture diagrams". |
| **4** | **Ubuntu / LPIC proof (optional)** | Link to your Ubuntu profile or "contributor" page; LPIC-1 (101) certificate scan or link if you want it cited. | Add URL or filename to §3 above; no need to commit certificate image. |
| **5** | **Runbook or backup procedure** (from your experience) | Short "when app is down we check X; when we backup we do Y" (even bullet points). | Paste into a note in `docs/private/` or send in chat; we turn it into the operator runbook and backup/restore text (PLAN_READINESS §4.3). |
| **6** | **Scenario one-liners** (case studies) | 1–3 sentences per scenario: e.g. "Empresa médio porte BR: 2 DBs PostgreSQL, 1 filesystem, foco LGPD Art. 37". | `docs/private/case_study_scenarios.md` or in chat. Feeds PLAN_LATO_SENSU §4.1–4.3. |
| **7** | **LGPD/ISO checklist** (if you have one) | Any checklist or list of "evidence we need" from a course, employer, or DPO template (generic is fine). | `docs/private/` or paste; we map app features to each line (PLAN_COMPLIANCE_EVIDENCE_MAPPING). |
| **8** | **Dockerfiles** (wf_t1r, uptk) | So we can say "Dockerfiles created and used" with a single reference. | `docs/private/Dockerfiles_used.md` (paste or paths) or ensure they're in the GitHub repos; add link in §1. |

**Not required:** Real customer data, confidential configs, or anything that would expose PII. Anonymised, synthetic, or "inspired by" is enough for thesis and evidence mapping.

### What you said you'll grab – quick checklist

Use this to tick off as you find or add each item. Store files in `docs/private/` unless noted.

| Item | Where to put it | Status (you can tick) |
| ---- | ----------------- | --------------------- |
| **RCDD BICSI** (cert or proof) | `docs/private/titulo-rcdd.jpeg` | ✅ Added |
| **PUC-RS IA e IoT** (cert PDF or PNG) | `docs/private/Certificado_IA_IOT_PucRS_Fabio.pdf` | ✅ Added |
| Program / course requirements (lato sensu) | `docs/private/` e.g. `program_tcc_requirements.pdf` | ⬜ |
| 1–2 redacted report excerpts (Data Boar) | `docs/private/` e.g. `sample_report_inventory.pdf`, `sample_heatmap.png` | ⬜ |
| Architecture diagram (high-level + pipeline) | `docs/topology-diagram.png` or thesis folder | ⬜ |
| Runbook or backup procedure (bullets) | `docs/private/` note or paste in chat | ⬜ |
| Scenario one-liners (case studies) | `docs/private/case_study_scenarios.md` or chat | ⬜ |
| LGPD/ISO checklist (if you have one) | `docs/private/` or paste | ⬜ |
| Dockerfiles note (wf_t1r, uptk) | `docs/private/Dockerfiles_used.md` or links in GitHub | ⬜ |
| **Learning / certs list** (paid incomplete; Udemy, Alura, etc.) | `docs/private/Learning_and_certs.md` – then use §3.1 sequenced to-do to prioritise and complete 1–2 | ⬜ |
| **DataPrev** (evidence of classification / 6th place) | `docs/private/` e.g. `DataPrev_exame_classificacao.pdf` or screenshot – for CV and narrative | ⬜ |

*(Optional)* Ubuntu/LPIC proof: add URL or filename to §3; no file needed if you only cite the link.

---

## 6. What else you can add (optional)

- **Dockerfiles:** From wf_t1r or uptk (or a short note in `docs/private/Dockerfiles_used.md`) so “Dockerfiles I created and used” is citable.
- **GitHub:** If you create a repo for uptk or add more public repos, add one line per repo in §2.
- **Certifications:** LPIC-2, cloud (AWS/GCP/Azure), security (e.g. CEH, CompTIA), or others – add a row in §3.
- **Community:** Ubuntu membership level, other FOSS projects, conference talks – add a row or link in §3.
- **Blog / articles:** Links and one-line description in §3.

When you add something, update this file and, if it affects narrative or evidence, mention it in TOKEN_AWARE_USAGE §3 or in the relevant plan (lato sensu, stricto sensu, compliance evidence).
