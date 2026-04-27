# Pares de scripts entre plataformas (Windows `.ps1` ↔ Linux/macOS `.sh`)

**English:** [SCRIPTS_CROSS_PLATFORM_PAIRING.md](SCRIPTS_CROSS_PLATFORM_PAIRING.md)

## Objetivo

Alguns **gates de desenvolvimento** e **wrappers finos** existem em **duas formas**: **PowerShell** (posto de trabalho principal histórico: Windows 11) e **bash** (Linux / macOS, shells parecidas com CI, colaboradores). Este documento é o **contrato** para manter **comportamento alinhado** quando qualquer lado muda — no mesmo espírito de **código → docs EN → docs pt-BR**, mas para **pontos de entrada de automação**.

**Relacionado:** **`.cursor/rules/repo-scripts-wrapper-ritual.mdc`**, **`docs/ops/TOKEN_AWARE_SCRIPTS_HUB.pt_BR.md`**, **`.cursor/skills/token-aware-automation/SKILL.md`**.

## Regras (mantenedores + assistentes)

1. **Scripts em par:** ao **acrescentar** ou **mudar comportamento** (flags, ordem dos passos, códigos de saída, *retry*) num membro do par, atualize o **par equivalente** no **mesmo PR** quando for prático; se não for, acrescente um **TODO rastreado** (por exemplo linha em **`PLANS_TODO.md`**) ligando os dois nomes de arquivo.
2. **Novo wrapper de gate:** se introduzires um **`scripts/*.ps1`** novo que operadores devam correr com frequência na raiz do repo, avalia se faz falta um **`scripts/*.sh`** para Linux — e o inverso se o primeiro for **`.sh`** em Linux e os contribuidores no Windows precisarem do mesmo fluxo.
3. **Nem tudo é par:** *scripts* só de lab **`*.sh`** (alvos SSH), só Windows (**`es-find.ps1`**) e orquestradores grandes podem ficar **numa só plataforma**; documenta isso na linha do hub ou no cabeçalho do script em vez de inventar um *twin* vazio.
4. **Comportamento de referência:** o **`.ps1`** continua a referência para a documentação *Windows-first* de hoje; o **`.sh`** espelha a **intenção** (`uv`, `pre-commit`, flags do `pytest`). Se houver deriva, corrige o código — não disfarces só com texto.

## Pares atuais (PC de desenvolvimento)

| Intenção | Windows | Linux / macOS |
| -------- | ------- | ------------- |
| Gate completo (*gatekeeper* + planos + *pre-commit* + *pytest*) | `scripts/check-all.ps1` | `scripts/check-all.sh` |
| Só *lint* / *hooks* | `scripts/lint-only.ps1` | `scripts/lint-only.sh` |
| Subconjunto *pytest* (`-Path` / `-Keyword`) | `scripts/quick-test.ps1` | `scripts/quick-test.sh` |
| *Pre-commit* + *pytest* completo (sem *gatekeeper* / sem *plans-stats*) | `scripts/pre-commit-and-tests.ps1` | `scripts/pre-commit-and-tests.sh` |
| Build do pré-filtro Rust Pro+ (`maturin develop` do `boar_fast_filter`) | `scripts/build-rust-prefilter.ps1` | `scripts/build-rust-prefilter.sh` |

**Nota:** o **`check-all.ps1`** chama **`gatekeeper-audit.ps1`** e **`plans-stats.py`** antes de delegar ao **`pre-commit-and-tests.ps1`**; o **`check-all.sh`** faz o mesmo ao nível do *shell*. Os **`pre-commit-and-tests.*`** ignoram *gatekeeper* e *plans-stats* de propósito.

**Twin do builder Rust:** `build-rust-prefilter.{ps1,sh}` rodam `maturin develop --manifest-path rust/boar_fast_filter/Cargo.toml`, têm `--release` como padrão e aceitam override de `--target`/`-Target`. O twin bash mapeia `-Release` ↔ `--release`, `-Debug`/`--no-release` ↔ profile debug, e `-Target X` ↔ `--target X`. Mantenha os dois alinhados ao adicionar flags (por exemplo *features* de cargo ou perfis adicionais).

## Verificação

- **Linux / CI:** `bash -n scripts/<nome>.sh` (ver **`tests/test_scripts.py`**).
- **Windows:** verificação de sintaxe PowerShell para **`*.ps1`** no mesmo módulo de testes.
