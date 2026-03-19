# Home lab: checagens de deploy e validação de alvos (manual)

**English:** [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md)

**Objetivo:** Executar **passos concretos** numa **segunda máquina** (VM ou host de containers) para comprovar **deploy**, **smoke** e **cobertura de conectores** com dados **sintéticos** e, opcionalmente, **reais** em pequena escala—sem depender só do CI ou do portátil de desenvolvimento.

**Não é aconselhamento jurídico.** Para dados **reais** de pessoas, exija **base legal**, **minimização** e contas técnicas **só leitura**; prefira dados **sintéticos** ou **amostras públicas** quando houver dúvida.

**Relacionado:** [deploy/DEPLOY.pt_BR.md](deploy/DEPLOY.pt_BR.md) · [SONARQUBE_HOME_LAB.md](SONARQUBE_HOME_LAB.md) · [OPERATOR_IT_REQUIREMENTS.pt_BR.md](OPERATOR_IT_REQUIREMENTS.pt_BR.md) · [TESTING.pt_BR.md](TESTING.pt_BR.md) · [SECURITY.pt_BR.md](../SECURITY.pt_BR.md)

---

## 0. Princípios

1. **Automatizar primeiro no repo:** `.\scripts\check-all.ps1` ou `uv run pytest -v -W error` na raiz.
1. **Lab = integração:** caminhos, volumes Docker, portas de BD, firewall.
1. **Sintético por omissão:** ficheiros `.txt` / `.csv` com padrões **falsos** (inspire-se nos testes do projeto, **não** use dados reais de terceiros).
1. **Real só com permissão:** cópias não produtivas, anonimizadas ou documentos seus.
1. **Containers Docker:** Prefira `docker run --rm` em checagens pontuais. Se mantiver um container **Data Boar** nomeado entre execuções, objetive **uma** instância principal—ou **duas** só para **A/B** explícito. Remova containers descartáveis ao fim para não confundir portas (`8088`) e volumes. Ver [DOCKER_SETUP.pt_BR.md](DOCKER_SETUP.pt_BR.md) §7.

---

## 1. Checklist base (copiar)

| Passo | Ação | Critério de sucesso |
| ----- | ---- | -------------------- |
| 1.1 | `git pull`; `uv sync` | Dependências OK |
| 1.2 | Testes completos | Tudo verde |
| 1.3 | `docker build -t data_boar:lab .` | Build concluído |
| 1.4 | `data/config.yaml` a partir de [config.example.yaml](../deploy/config.example.yaml) | YAML válido |
| 1.5 | `docker run` com volume `/data` e `CONFIG_PATH` | Dashboard em `:8088`, `/health` OK |
| 1.6 | Scan com `targets: []` | Termina sem crash |

---

## 2. Filesystem sintético

Crie um diretório no host, ficheiros `notes.txt` / `sheet.csv` com CPF/e-mail **de teste**; monte em `/data/...`; defina alvo `type: filesystem` como em [HOMELAB_VALIDATION.md §2](HOMELAB_VALIDATION.md#2-synthetic-filesystem-target-fastest-real-connector-test).

---

## 3. SQLite como ficheiro

Pequena base `.db` com tabela de texto sintético; `scan_sqlite_as_db` ou alvo database conforme [USAGE.md](USAGE.md).

---

## 4. PostgreSQL / MySQL em Docker

Suba contentor na mesma rede Docker que a app; utilizador **read-only** se possível; alvo `database` com host = nome do serviço. Detalhes: [HOMELAB_VALIDATION.md §4](HOMELAB_VALIDATION.md#4-postgresql-or-mysqlmariadb-in-docker-lab-sql).

---

## 5. NoSQL (opcional)

MongoDB / Redis com extra `nosql` em [pyproject.toml](../pyproject.toml); dados sintéticos.

---

## 6. API REST (opcional)

Mock trivial no lab; validar conector API.

---

## 7. Arquivos compactados

`scan_compressed` + ZIP; extra `compressed` para `.7z`. Ver [HOMELAB_VALIDATION.md §7](HOMELAB_VALIDATION.md#7-compressed-archives-scan_compressed).

---

## 8. Licenciamento (opcional)

Modo `enforced` sem `.lic` deve bloquear; ver [LICENSING_SPEC.md](LICENSING_SPEC.md).

---

## 9. SonarQube (opcional)

[SONARQUBE_HOME_LAB.md](SONARQUBE_HOME_LAB.md) — qualidade de código, não conectividade de dados.

---

## 10. Registar resultados

Nota datada (ex.: `docs/private/` ignorado pelo git): tag da imagem, alvos, pass/fail.

---

## 11. Ver também

- [PLANS_TODO.md](plans/PLANS_TODO.md) — sequência token-aware após o lab.
- [CODE_PROTECTION_OPERATOR_PLAYBOOK.md](CODE_PROTECTION_OPERATOR_PLAYBOOK.md) — Priority band A.
