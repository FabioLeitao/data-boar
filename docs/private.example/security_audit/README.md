# `security_audit` — local PII seed bundle (template)

**Tracked copy-me.** Real seeds and classification notes must live under **`docs/private/security_audit/`**, which is **gitignored** and **not** created by `git clone` of the public product repo.

## Bootstrap (any machine)

From repo root:

```bash
mkdir -p docs/private/security_audit
cp docs/private.example/security_audit/PII_LOCAL_SEEDS.example.txt docs/private/security_audit/PII_LOCAL_SEEDS.txt
# Edit PII_LOCAL_SEEDS.txt: one literal string per line for git pickaxe / fixed-string grep.
```

```powershell
New-Item -ItemType Directory -Force -Path docs/private/security_audit | Out-Null
Copy-Item docs/private.example/security_audit/PII_LOCAL_SEEDS.example.txt docs/private/security_audit/PII_LOCAL_SEEDS.txt
# Edit PII_LOCAL_SEEDS.txt: one literal string per line.
```

Optional: maintain **`PII_CONTEXT_DECISIONS_LOG.pt_BR.md`** (or another private log) next to the seeds file for `ACEITAVEL` vs `VAZAMENTO` notes.

## Why Linux looked “broken”

Commands such as `grep docs/private/security_audit/PII_LOCAL_SEEDS.txt` fail with **No such file or directory** until you **copy** the example (or receive the real file from the maintainer’s private channel). This is expected on a fresh clone.

## References

- Public cadence and gates: **[docs/ops/PII_VERIFICATION_RUNBOOK.md](../../ops/PII_VERIFICATION_RUNBOOK.md)** ([pt-BR](../../ops/PII_VERIFICATION_RUNBOOK.pt_BR.md))
- Policy: **[docs/PRIVATE_OPERATOR_NOTES.md](../../PRIVATE_OPERATOR_NOTES.md)**
