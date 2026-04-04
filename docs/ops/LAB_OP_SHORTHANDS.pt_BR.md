# Shorthands do LAB-OP (taxonomia + wrappers seguros)

**English:** [LAB_OP_SHORTHANDS.md](LAB_OP_SHORTHANDS.md)

## Objetivo

Dar comandos “memória muscular” para fluxos do LAB-OP, sem incentivar atalhos inseguros.

## Taxonomia

- **report**: roda `homelab-host-report.sh` (inventário + snapshot de postura)
- **report-all**: roda o report em todos os hosts do manifest privado
- **sync-collect**: (opcional) `git pull` em cada clone e depois o report (multi-host)

## Wrapper shorthand

Use `scripts/lab-op.ps1` como entry point estável:

```powershell
.\scripts\lab-op.ps1 -Action report -SshHost latitude
.\scripts\lab-op.ps1 -Action report-all
.\scripts\lab-op.ps1 -Action report-all -Privileged -Deep
.\scripts\lab-op.ps1 -Action sync-collect -SkipFping
```

## Guardrails

- Probes privilegiados são **opt-in** (`--privileged` / `-Privileged`).
- Checagens “deep” são **opt-in** (`--deep` / `-Deep`) e podem aumentar tempo/ruído.
- Não adicione `NOPASSWD` amplo; veja [LAB_OP_PRIVILEGED_COLLECTION.pt_BR.md](LAB_OP_PRIVILEGED_COLLECTION.pt_BR.md) para o padrão restrito.

