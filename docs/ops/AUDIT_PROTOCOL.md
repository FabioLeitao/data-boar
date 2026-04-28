# Data Boar Audit Protocol (Agent Governance Dump)

## Purpose

This protocol defines a reproducible "truth serum" dump for external audits of
agent behavior and governance infrastructure in Data Boar.

The dump captures one consolidated `.txt` with:

- agent governance surfaces (`AGENTS.md`, rules, skills),
- CI/editor posture (`.github`, `.vscode`, pre-commit),
- operational doctrine and rituals (`docs/ops/inspirations`),
- wrapper/gate scripts (`check-all`, `pre-commit-and-tests`, related scripts).

It is designed for transparency and troubleshooting before support escalations,
security triage, or strategic reviews.

## Scripts

- Windows/PowerShell: `scripts/dump-context.ps1`
- Linux/macOS Bash: `scripts/dump-context.sh`

Default output: `data-boar-blackbox-audit.txt` at repo root.

## Privacy Contract (Strict)

Both scripts must strictly exclude:

- any path containing a directory segment named `private`,
- any file whose basename starts with `.env`.

This protects local secrets and private operator context from audit bundles.

## File Boundary Contract

Every captured file must include explicit boundaries:

- `#### START_FILE: <relative/path> ####`
- metadata lines (`TIMESTAMP`, `PERMISSIONS` when available, `SIZE_BYTES`)
- `#### END_FILE: <relative/path> ####`

This makes the dump deterministic and diff-friendly for external reviewers.

## Linux Sync Integrity Check

The Bash script validates local git state against `origin/<branch>` (or `@{u}`
fallback) and records a sync status line in the dump:

- `SYNC_OK: ...` when aligned
- `WARNING: ...` when local HEAD diverges or cannot be validated

This avoids cross-environment drift during audit handoffs.

## When To Run

Run the dump before:

- support escalation,
- external review of agent behavior,
- strategic governance/risk assessment,
- post-incident evidence packaging.

## Usage

From repo root:

```powershell
.\scripts\dump-context.ps1
```

```bash
./scripts/dump-context.sh
```

Optional custom output file:

```powershell
.\scripts\dump-context.ps1 -OutputFile "audit-2026-04-28.txt"
```

```bash
./scripts/dump-context.sh audit-2026-04-28.txt
```

## Validation Expectation

Changes to these scripts should pass repository lint/gates (`check-all` or
`lint-only`) and avoid risky patterns (no command injection helpers, no dynamic
eval, no secret scraping behavior).
