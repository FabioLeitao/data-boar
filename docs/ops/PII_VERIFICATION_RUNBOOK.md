# PII Verification Runbook

Operational runbook for public-repo PII/sensitive-data verification with a short, mid, and long cadence.

## Manual review gate (required)

Before marking any run as SAFE, review the local/private criteria that are intentionally not stored in tracked docs.

- [ ] I reviewed the current local criteria in `docs/private/security_audit/` (that path is **not** in a public clone; bootstrap from [`docs/private.example/security_audit/`](../private.example/security_audit/README.md) or another maintainer channel).
- [ ] I updated local allow/deny seeds (if needed) in private notes/files.
- [ ] I confirmed no new sensitive identifiers should be added to tracked guardrails.

If any item is unchecked, **do not** mark SAFE.

## Scope and intent

- This runbook covers tracked files and Git history in a **fresh clone**.
- It complements guardrails (`new-b2-verify`, `pii_history_guard.py`, `test_pii_guard.py`).
- It does not replace manual classification for contextual terms.
- `new-b2-verify.ps1` is PowerShell-only (best on L14/Windows). On Linux hosts, use the manual equivalent below.

## 0) Preconditions

Run in a fresh clone:

```powershell
cd C:\temp
if (Test-Path .\teste_operator_fresh) { Remove-Item -Recurse -Force .\teste_operator_fresh }
mkdir teste_operator_fresh | Out-Null
cd .\teste_operator_fresh
git clone git@github.com:FabioLeitao/data-boar.git
cd .\data-boar
git status
```

Expected: clean tree on `main`.

### Linux (lab-op hosts)

```bash
cd /tmp
rm -rf teste_operator_fresh
mkdir -p teste_operator_fresh
cd teste_operator_fresh
git clone git@github.com:FabioLeitao/data-boar.git
cd data-boar
git status
```

Expected: clean tree on `main`.

### Private `security_audit` bundle (missing after clone)

`docs/private/` is **gitignored**; a normal `git clone` does **not** create `PII_LOCAL_SEEDS.txt`. If `grep` or `mapfile` fails with **No such file or directory**, seed the folder first:

```bash
mkdir -p docs/private/security_audit
cp docs/private.example/security_audit/PII_LOCAL_SEEDS.example.txt docs/private/security_audit/PII_LOCAL_SEEDS.txt
# Edit PII_LOCAL_SEEDS.txt with maintainer-approved literals (one per line).
```

```powershell
New-Item -ItemType Directory -Force -Path docs/private/security_audit | Out-Null
Copy-Item docs/private.example/security_audit/PII_LOCAL_SEEDS.example.txt docs/private/security_audit/PII_LOCAL_SEEDS.txt
# Edit PII_LOCAL_SEEDS.txt with maintainer-approved literals (one per line).
```

## 1) Short run (weekly / before sensitive PRs)

```powershell
.\scripts\new-b2-verify.ps1 -TargetUserSegment fabio
uv run python .\scripts\pii_history_guard.py
uv run pytest tests/test_pii_guard.py -q
# Run the UC-pattern grep from your local/private criteria bundle.
git grep -n -E "\b(192\.168\.[0-9]{1,3}\.[0-9]{1,3}|10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3})\b" -- scripts docs tests .cursor
git grep -n -E "\b[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}\b" -- scripts docs tests .cursor
```

Pass condition: no relevant matches + tests pass.

### Linux (`new-b2-verify.ps1` equivalent)

```bash
TARGET_SEGMENT="fabio"
TARGET_PATH_UPPER="C:\\Users\\${TARGET_SEGMENT}"
TARGET_PATH_LOWER="c:\\users\\${TARGET_SEGMENT}"

git log --all -S "${TARGET_PATH_UPPER}" --oneline
git log --all -S "${TARGET_PATH_LOWER}" --oneline
git grep -n -i -F "${TARGET_PATH_UPPER}" $(git rev-list --all)

uv run python ./scripts/pii_history_guard.py
uv run pytest tests/test_pii_guard.py -q
# Run the UC-pattern grep from your local/private criteria bundle.
git grep -n -E "\b(192\.168\.[0-9]{1,3}\.[0-9]{1,3}|10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3})\b" -- scripts docs tests .cursor
git grep -n -E "\b[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}\b" -- scripts docs tests .cursor
```

## 2) Mid run (monthly)

```powershell
git grep -n -E "linkedin\.com/in/" -- . ":(exclude)docs/private/**"
git grep -n -i -E "c:\\users\\[^\\]+|/home/[^/]+" -- . ":(exclude)docs/private/**"
```

Then classify each hit as:

- acceptable placeholder/test/example; or
- real sensitive exposure requiring immediate fix.

## 3) Long run (quarterly or post-incident)

Run full-history checks for high-risk seeds relevant to your private policy:

```powershell
git log --all -S "C:\Users\fabio" --oneline
git log --all -S "c:\users\fabio" --oneline
git log --all -S "/home/leitao" --oneline
git log --all -S "linkedin.com/in/" --oneline
# Run the UC seed check from your local/private criteria bundle.
```

Keep any person-specific or case-specific seeds in private notes/files only.

## Context-sensitive terms (manual classification)

Some terms may be allowed only in narrow contexts (for example, career portfolio context) and not in legal/medical/private contexts.

When such terms appear:

1. classify by context;
2. document the decision in private notes;
3. fix tracked files if context is not allowed.

## Final SAFE decision

Mark SAFE only if:

- manual review gate is fully checked;
- short run passes;
- mid/long checks show no real exposure;
- contextual terms were manually classified.

If any criterion fails, status is NOT SAFE and requires a surgical remediation + re-run.
