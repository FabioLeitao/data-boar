# Completão — prompt-mestre de checklist de release (arquivo do operador)

**English:** [COMPLETAO_MESTRE_RELEASE_CHECKLIST_PROMPT.md](COMPLETAO_MESTRE_RELEASE_CHECKLIST_PROMPT.md)

## Objetivo

Guardar o **prompt completo** de validação **1.7.3** (papel SRE / Lab-Op) **antes de qualquer execução** — como referência versionada para colar, comparar ou enxugar. **Atalho em chat novo:** linha 1 **`completao`**, linha 2 **`tier:release-master-v1-7-3`**, ou **`.\scripts\completao-chat-starter.ps1 -Tier release-master-v1-7-3`**. Para **outras releases**, use **`.\scripts\completao-chat-starter.ps1 -Tier release-master -ReleaseSemver X.Y.Z`** (opcional **`-GitTag`**) e, ao arquivar, acrescente **`COMPLETAO_MESTRE_RELEASE_CHECKLIST_PROMPT_<semver>.md`** (+ **`.pt_BR.md`**) — o starter prefere esse arquivo quando existir. Ver **[`COMPLETAO_OPERATOR_PROMPT_LIBRARY.pt_BR.md`](COMPLETAO_OPERATOR_PROMPT_LIBRARY.pt_BR.md)**.

## Alinhamento de política (ler antes de executar)

As notas de **caminhos versionados vs privados**, **clone principal Windows**, e **caminho canônico do script de corpus** estão na seção **Policy alignment** da versão em inglês (fonte bilingue para estes avisos técnicos): [COMPLETAO_MESTRE_RELEASE_CHECKLIST_PROMPT.md](COMPLETAO_MESTRE_RELEASE_CHECKLIST_PROMPT.md).

## Texto-mestre verbatim (v1.7.3 — arquivo 2026)

```text
🐗 [PROMPT MESTRE PARA O AGENTE: EXECUÇÃO DO COMPLETÃO v1.7.3]
"Agente, você é o SRE líder do Lab-Op. Sua missão é validar a Release 1.7.3 do Data Boar. A consistência de versões entre os nodes é sua prioridade absoluta. Antes de começar, leia docs/ops/OPERATOR_AGENT_COLD_START_LADDER.md para situar sua memória.

Siga esta sequência utilizando a sessão tmux 'completao' (sudo warm) ativa com -privileged. Você tem permissão de realizar ajustes safe e least privileged necessários nos OSs, serviços e aplicações no Lab-Op, use ansible, opentofu ou comandos de pacote do OS (apt/xbps/winget) conforme necessário.

FASE 0: Teste de go/no-go (Reconhecimento de Terreno)

Avalie se conhece os hardwares do lab-op e se respondem a ICMP.

Confirme acesso via SSH e credenciais no ~/.ssh/config.

Atenção: Consulte docs/ops/LAB_OP_HOST_PERSONAS.md para entender o papel de cada máquina antes de tocar nelas.

Lembre-se: Path canônico no Linux é /home/leitao/Projects/dev/data-boar. No Windows dev workstation (principal), use WSL2.

Temos contratos de sudo passwordless ativos. Use-os.

FASE 1a: Sincronização e Inventário (Anti-Drift)

Git Sync Global: Em todos os nodes (Windows dev workstation, Latitude, T14, Mini-BT, Pi3B), execute: git fetch --all --tags && git checkout tags/v1.7.3.

Garanta branch main (ou tag v1.7.3) com git pull limpo. O comando git describe --tags deve retornar exatamente v1.7.3.

Fallback de Rede: Se o Pi3B ou outro falhar por timeout, use o Windows dev workstation para enviar o repositório via scp -r ou rsync para o nó. Paridade total é mandatória.

Confira no pyproject.toml se a versão descrita é a 1.7.3.

Sincronia de Imagens: Garanta a imagem fabioleitao/data_boar:1.7.3. No T14 (Podman) e no Windows dev workstation (Docker Swarm/WSL2), force o pull ou verifique o Digest da v1.7.3.

Ajuste Mini-BT: Tente xbps-install -S libmariadbclient-devel. Se falhar, documente e não tente testar o componente DB neste nó, pois o uv sync falhará.

FASE 1b: Registro do Estado Atual

Mapeamento de Recursos: Gere o arquivo docs/ops/LAB_OP_STATE.md.

Catalogue: Hardware/OS, Runtimes (docker, podman, python3, uv, pip).

Se detectar limitações (ex: falta de Python no T14), autoajuste as fases seguintes respeitando a Persona do host (T14 = Enterprise/Podman only).

FASE 2a: Setup da Infraestrutura e Dados Sintéticos

Geração de PII (no Windows dev workstation): Utilize o script tests/data/generate_synthetic_poc_corpus.py.

Plano A: uv run python scripts/generate_synthetic_poc_corpus.py --output ./samples

Plano B (Fallback): uv run --with pillow --with openpyxl --with python-docx --with reportlab python scripts/generate_synthetic_poc_corpus.py --output ./samples

Plano C (Pip): pip install pillow openpyxl python-docx reportlab && python scripts/generate_synthetic_poc_corpus.py --output ./samples

Distribuição: Assim que gerados no Windows dev workstation, envie para /home/leitao/samples/ em todos os nodes via scp ou rsync.

Database Stack: No Latitude, suba o Swarm (scripts/stack-db.yml) e confirme se os bancos estão prontos.

Mounts: No T14, prepare o mount de rede para os documentos do Latitude em /mnt/latitude_docs. Valide o mount.

Gestão de Recursos: Se houver gargalo, distribua os DBs entre T14 e Latitude conforme necessário, adaptando o target dos testes.

FASE 2b: Compartilhamento de Redes e Latência

Prepare protocolos compatíveis (NFS, SMB/CIFS, SSHFS) mesmo nas máquinas lentas (Pi3B) para validar conectividade e capacidade de operar com latências extremas ou hardware antigo.

FASE 3a: Execução do 'Completão' (SSH/tmux sessão 'completao')

Node T14 (LMDE 7 - Persona Enterprise): Use estritamente podman run. Mapeie /tmp/config_databoar.yaml, a pasta de samples e a porta da API -p 8080:8080.

Node Latitude (Zorin 18 - Persona Pro): Execute via uv run (source) E via Docker para validar paridade. Escaneie /home/leitao/documents (Cifras) e /var/log.

Node Pi3B (Trixie - Persona Legacy): Scan local (/var/log) via Python nativo. Monitore impacto de IO/RAM e colete dmesg/syslog pós-teste em busca de OOM Kills.

Node Windows dev workstation (Win11): Scan via WSL2 e via Windows nativo.

Node Mini-BT (Void): Scan local de arquivos; ignore DB se a lib-mysql falhou na Fase 1.

FASE 3b: Execução via API e Web

Valide Health Check via curl no status da API.

Inicie escaneamento via API, confirme status de 'scanning' e aguarde o 'idle' para baixar o report.

Rate Limit: Tente comandar sessões com intervalo curtíssimo para confirmar se a proteção anti-pattern no config.yaml bloqueia o abuso.

Security by Design: Verifique presença de security headers e HTTPS onde configurado (especialmente no T14/Latitude).

dashBOARd: Acesse a interface web onde disponível, valide reports e tente injeções simples (SQL-i) nos campos de argumentos para testar sanitização.

FASE 4: Auditoria e Report Final

Heurística: Garanta que cifras de música no Latitude foram classificadas como 'Inócuas'.

Consistência: Verifique se a PII sintética foi detectada igualmente em todas as plataformas.

Erros Propositais: Valide se mensagens de erro (DB offline, IP inválido) são úteis para o operador.

Consolidação: Reúna os resultados em docs/reports/TEST_REPORT_v1.7.3.md.

Sucesso: Se 'ALL GREEN' (paridade total e 0 leaks), declare pronto para 1.7.4-beta.

REGRAS OPERACIONAIS CRÍTICAS:

Dispare orquestração via scripts/lab-completao-orchestrate.ps1 quando aplicável.

Gere config.yaml efêmeros em /tmp/ baseados no techguide.md. Inclua o próprio path do repo como target de scan para "comer a própria comida".

Use sudo -v warm. Se o SSH falhar, tente 3x antes de reportar.

Priorize a integridade do Windows dev workstation; ele é sua base de comando. SRE coleta evidências e aprende com as falhas."
```

---

## Ligações

- **[`COMPLETAO_OPERATOR_PROMPT_LIBRARY.pt_BR.md`](COMPLETAO_OPERATOR_PROMPT_LIBRARY.pt_BR.md)** — taxonomia **`tier:`** + **`completao-chat-starter.ps1`**
- **[`LAB_COMPLETAO_RUNBOOK.pt_BR.md`](LAB_COMPLETAO_RUNBOOK.pt_BR.md)** — contratos e ordem de fatias
- **[`LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md`](LAB_COMPLETAO_FRESH_AGENT_BRIEF.pt_BR.md)** — blocos A–E
