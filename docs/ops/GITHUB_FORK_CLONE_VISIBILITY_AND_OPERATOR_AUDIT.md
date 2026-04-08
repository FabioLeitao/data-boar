# GitHub: fork visibility, clone visibility, and what you must do locally

**Português (Brasil):** [GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.pt_BR.md](GITHUB_FORK_CLONE_VISIBILITY_AND_OPERATOR_AUDIT.pt_BR.md)

**Purpose:** State **facts** about what GitHub exposes (and does **not** expose) so you do not assume there is a “list of everyone who cloned.” Pair with **[PII_DEFINITIVE_REMEDIATION.md](PII_DEFINITIVE_REMEDIATION.md)** for cleanup steps.

---

## 1. Forks — **auditable**

GitHub exposes **public forks** of a public repository. You can list them.

**GitHub CLI** (authenticated):

```bash
gh api repos/FabioLeitao/data-boar/forks --paginate --jq '.[] | {owner: .owner.login, full_name, pushed_at, updated_at}'
```

**Browser:** open the repo → **Insights** → **Network** (fork graph), or the **Forks** count on the repo home page.

**Who may hold a full copy:** each fork owner’s GitHub fork object database (until they delete the fork or reset it to match your current `main`).

**Your minimal action:** identify each fork; contact the owner if an outdated fork still carries pre-remediation history; they must delete or re-fork / hard-reset from your `main` — you cannot delete someone else’s fork from your account.

---

## 2. `git clone` — **not** a per-user audit trail on GitHub

For a **public** repository, GitHub **does not** publish:

- a list of GitHub users who ran `git clone`
- IP addresses of anonymous `git clone` operations
- machine-by-machine inventory of clones

**Why:** `git clone` against `https://github.com/...` or `git@github.com:...` does not register a stable “clone registry” you can download as the repo owner.

**What exists for owners (limited):**

- **Insights → Traffic** (repo settings): **clone** counts are **aggregate** (e.g. clones per day), not “who.” Availability depends on GitHub product and your role on the repo.
- **Stars / watchers** show **accounts** that interacted in those ways — not equivalent to clones.

**Who may hold a full copy:** anyone who ever cloned while the old history was on `origin` (any machine worldwide, any mirror). You will **not** get a complete list from GitHub.

**Your minimal action:** treat “unknown clones” as **out of scope** for exhaustive audit; focus on **forks you can see**, **collaborators you know**, and **machines you control** (see §4).

---

## 3. Mirrors and CI

- **Third-party mirrors** (if any) are outside GitHub’s fork list.
- **GitHub Actions** checkouts are ephemeral; they do not replace “who has a local clone.”
- **Long-lived caches** elsewhere (corporate proxy, personal backup) are not visible from GitHub.

---

## 4. Minimal checklist — **only what you must do on your side**

| Step | Action |
| ---- | ------ |
| 1 | Run **`gh api .../forks`** (or use the web UI) and **record** every fork `full_name` and `pushed_at`. |
| 2 | For each fork that still matters: **message the owner** — align with current `main` or delete the fork (you cannot do this for them). |
| 3 | **Inventory your own devices** where you (or people you trust) cloned the repo: dev PC, laptops, lab hosts — **list in your private notes**, not in this public doc. On each: `git fetch origin && git reset --hard origin/main` when you intend to match GitHub. |
| 4 | **Optional:** open **Insights → Traffic** on GitHub (if available) for **trend** awareness only — not a list of cloners. |
| 5 | Accept that **anonymous clones** of a public repo **cannot** be fully audited; risk reduction is **history rewrite on canonical repo + forks you control + known machines**. |

---

## 5. Related docs

- [PII_DEFINITIVE_REMEDIATION.md](PII_DEFINITIVE_REMEDIATION.md) — force-push, `filter-repo`, clone reset.
- [PII_VERIFICATION_RUNBOOK.md](PII_VERIFICATION_RUNBOOK.md) — local seeds and grep cadence (private files).
