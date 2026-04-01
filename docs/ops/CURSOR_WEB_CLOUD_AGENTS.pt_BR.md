# Cursor Web / Cloud Agents — visibilidade, segurança e captura de evidências

**English:** [CURSOR_WEB_CLOUD_AGENTS.md](CURSOR_WEB_CLOUD_AGENTS.md)

## Objetivo

Usar Cursor Web / Cloud Agents para **reduzir toil** (sandbox reproduzível), sem:

- vazar segredos,
- confundir comportamento LAN-only (LAB-OP),
- ou queimar tokens com gates pesados sem necessidade.

## Cloud Agents precisam de commits / PRs para “ver” mudanças?

**Regra prática de visibilidade:**

- **Mudanças locais não commitadas**: Cloud Agents **não** veem.
- **Commits locais não enviados (push)**: Cloud Agents **não** veem.
- **Commits enviados (push) para um branch**: Cloud Agents **podem** ver (eles puxam do repo remoto).
- **PRs**: não são estritamente necessários para visibilidade, mas são **recomendados** para:
  - contexto revisável,
  - evidência via CI,
  - e um “paper trail” durável (estilo SRE).

Ou seja: **push é obrigatório**, PR é **opcional (mas quase sempre vale)**.

## Restrições de segurança

- **Sem segredos** em:
  - setup/update scripts,
  - arquivos commitados,
  - ou descrições de PR.
- Cloud Agents não substituem acesso à **LAN do operador** nem fluxos com `docs/private/`.

Fonte de verdade: `.cursor/rules/cloud-agents-token-aware-safety.mdc`.

## Gates token-aware

Refresh padrão (barato):

- `uv sync`
- `uv run pre-commit run --all-files`

Gates pesados só em marcos:

- pré-PR / pré-merge
- pré-version bump / pré-release / pré-publish
- pré-WRB (quando você quer “all green” como evidência)

## Troubleshooting de rede (quando Chat/Agent falham no LAB mas passam na DMZ/hotspot)

Se o Cursor Network Diagnostic mostra:

- **Chat** falhando com “streaming responses are being buffered by a proxy…”
- **Agent** falhando com “bidirectional streaming is not supported by the http2 proxy…”

e ao mesmo tempo **na DMZ ou hotspot do iPhone** tudo passa, então o problema está **no caminho de rede do LAB-ROUTER-01/SSID/VLAN** (não no Windows).

### Checklist rápido (LAB-ROUTER-01 / UniFi Network) — ordem mais provável

1) **Traffic Routes / Policy-based routing (VPN client / rota especial)**
   - Procure regras que façam o SSID/VLAN “<SSID_NAME>” sair por algum túnel/rota diferente.
   - Desative a regra temporariamente e reteste o Diagnostic.

2) **Threat Management (IDS/IPS)**
   - Teste colocar em “Detect only” (ou Off por 2 min) e reteste.
   - Se resolver, o fix final é ajustar o perfil/assinaturas, não deixar Off.

3) **Ad Blocking / Content filtering / DNS Shield (se ativados)**
   - Desative temporariamente e reteste (só para isolar causa).

4) **Smart Queues / QoS / Traffic shaping agressivo (se houver)**
   - Desative temporariamente e reteste.

### Evidência SRE

- Guarde 2 screenshots: Diagnostic **falhando** no SSID “<SSID_NAME>” e **passando** na DMZ/hotspot.
- Registre o “toggle” que resolveu (qual item do checklist acima).

## Captura de evidências (hábito SRE)

Trate output do Cloud Agent como output de CI:

- guarde o link do run (ou screenshots) como **evidência**
- logs sensíveis ficam **somente** em `docs/private/`
- resumos redigidos podem ir em docs rastreadas quando fizer sentido

Template privado: `docs/private.example/cursor_web/README.md` (copie para `docs/private/cursor_web/`).

