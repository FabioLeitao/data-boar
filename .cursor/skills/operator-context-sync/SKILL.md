# Skill: operator-context-sync

## When to use

When the operator shares **new factual information** about themselves that should update the assistant's understanding:
- New employer, role change, or career transition
- New certifications, publications, or achievements
- Change in family/personal situation relevant to work context
- IP declarations, contracts, or formal commitments
- Health events, significant life events, recovery milestones
- Changes in financial situation or project funding

This skill is also invoked when the operator uploads raw files (PDFs of emails, welcome letters, contracts, LinkedIn exports) and wants the assistant to **absorb and record** the new context.

## Session keyword

`operator-sync` — When operator types this, immediately run steps below.

## Step-by-step workflow

### Step 1: Gather new facts

If raw files (PDFs) were provided:
- Read them with the Read tool
- Extract: employer, role, start date, key context, any IP/legal declarations

If facts were stated in chat:
- Note them with high precision (dates, names, titles matter)

### Step 2: Identify files to update

Always check and update (if relevant):

| File | What to update |
|---|---|
| `docs/private/homelab/OPERATOR_RETEACH.md` | Add new dated section (e.g. `## C. Nova info — YYYY-MM-DD`) |
| `docs/private/author_info/OPERATOR_CONTEXT_FOR_AGENT.pt_BR.md` | Update "Identidade profissional" section |
| `docs/private/FABIO_GOALS_MASTER.pt_BR.md` | Update "Estado atual" under relevant goal |
| `docs/private/author_info/STRATEGIC_ALIGNMENT_MASTER.pt_BR.md` | Update trajetoria table + "Empregador atual" |

Optional (if facts are deep personal context):
- `docs/private/author_info/PERSONAL_JOURNAL.pt_BR.md` (if it exists) — add dated entry

### Step 3: Write updates using PowerShell (preferred)

Avoid StrReplace for files with encoding/special chars. Use:

```powershell
$content = Get-Content $path -Raw -Encoding UTF8
$content = $content -replace 'old pattern', 'new text'
Set-Content -Path $path -Value $content -Encoding UTF8
```

Or append a new section:

```powershell
$newSection = @"
---
## D. Atualizacao — $(Get-Date -Format 'yyyy-MM-dd')

- **Fato:** [descrever]
"@
Add-Content -Path $path -Value $newSection -Encoding UTF8
```

### Step 4: Verify

After updating, read back 10-20 lines around the change to confirm correctness.

### Step 5: Notify operator

Report which files were updated and what was changed.

## Guardrails

- **Never** put real passwords, tokens, or secret keys in any file (tracked or private).
- **Never** put real LAN IPs, hostnames, or hardware serials in tracked files.
- **Only** update files under `docs/private/` (gitignored) — never in tracked docs.
- If a PDF contains sensitive financial/legal data, note the key facts but do NOT paste the full document content into any file.
- Dates matter: always use ISO format `YYYY-MM-DD` in updates.

## Example: new employer update

If operator says "I just started at Company X as Role Y":
1. Add section to OPERATOR_RETEACH.md:

   ```
   ## D. Emprego novo — 2026-XX-XX
   - Cargo: Role Y
   - Empresa: Company X
   - Inicio: [data]
   - Contexto: [breve descricao]
   ```

2. Update OPERATOR_CONTEXT_FOR_AGENT.pt_BR.md identity section
3. Update FABIO_GOALS_MASTER.pt_BR.md "Estado atual" under career goal
4. Update STRATEGIC_ALIGNMENT_MASTER.pt_BR.md trajetoria table

## Token-aware mode

If operator says `short` or `token-aware`:
- Read only OPERATOR_RETEACH.md (smallest, fastest to update)
- Defer STRATEGIC_ALIGNMENT_MASTER updates to next dedicated session
- One update per file maximum

## References

- `docs/private/homelab/OPERATOR_RETEACH.md`
- `docs/private/author_info/OPERATOR_CONTEXT_FOR_AGENT.pt_BR.md`
- `docs/private/FABIO_GOALS_MASTER.pt_BR.md`
- `docs/private/author_info/STRATEGIC_ALIGNMENT_MASTER.pt_BR.md`
- `docs/ops/OPERATOR_SESSION_CAPTURE_GUIDE.md` (broader session capture workflow)
