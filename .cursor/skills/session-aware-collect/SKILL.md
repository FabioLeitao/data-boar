# Skill: session-aware-collect

**Proposito:** Coletar dados periodicos de servicos externos (Growatt, Enel, LinkedIn, redes sociais)
usando sessoes autenticadas do browser Cursor, de forma segura e token-aware.

**Quando usar:**
- Operador pede coleta semanal de dados solares Growatt
- Operador pede verificacao mensal de consumo Enel
- Verificar progresso ATS de colaboradores no LinkedIn apos dicas enviadas
- Varredura mensal de redes sociais para contexto do founder/pool

---

## Wrapper CLI (USE PRIMEIRO)

```powershell
# Status de todas as sessoes e frequencias
.\scripts\session-collect.ps1 -Service status

# Coletar tudo que esta na janela (baseado em intervalos)
.\scripts\session-collect.ps1

# Forcar coleta especifica (ignora intervalo)
.\scripts\session-collect.ps1 -Service growatt -Force
.\scripts\session-collect.ps1 -Service enel -Force
.\scripts\session-collect.ps1 -Service linkedin
.\scripts\session-collect.ps1 -Service social

# Growatt especifico
.\scripts\growatt-session-collect.ps1 -Mode check   # verifica sessao
.\scripts\growatt-session-collect.ps1 -Mode today   # dados de hoje
.\scripts\growatt-session-collect.ps1 -Mode month   # mes atual
.\scripts\growatt-session-collect.ps1 -Mode save    # coleta e salva

# Enel (READ-ONLY guardrail ativo)
.\scripts\enel-session-collect.ps1 -Mode check      # verifica sessao
.\scripts\enel-session-collect.ps1                   # resume dados locais
.\scripts\enel-session-collect.ps1 -Mode invoices    # historico de faturas

# iCloud Photos (download seletivo para analise)
.\scripts\icloud-photos-fetch-range.ps1 -Start "2022-11-01" -End "2022-11-30"
.\scripts\icloud-photos-fetch-range.ps1 -Start "2025-01-01" -End "2025-06-30" -MaxFiles 50
.\scripts\icloud-photos-fetch-range.ps1 -Cleanup   # remove temp apos analise
```

---

## Arquitetura de Sessoes

```
docs/private/homelab/
  .env.growatt.session    # GROWATT_SESSION=<JSESSIONID>  (expira em horas/dias)
  .env.enel.session       # ENEL_SESSION=<ASP.NET_SessionId> (expira em horas)
  session-collect-state.json  # ultima coleta por servico
```

**Frequencias:**

| Servico  | Frequencia | Script                        | Guardrail |
|----------|-----------|-------------------------------|-----------|
| Growatt  | Semanal   | growatt-session-collect.ps1   | Nenhum (GET apenas) |
| Enel     | Mensal    | enel-session-collect.ps1      | CRITICO: nunca submeter formularios |
| LinkedIn | Quinzenal | talent.ps1 linkedin <alias>   | Respeitar rate limits |
| Redes sociais | Mensal | browser manual + screenshot | 300s timeout por rede |
| iCloud   | Por demanda| icloud-photos-fetch-range.ps1 | Max 200 fotos / Cleanup depois |

---

## Como Exportar Cookies do Browser Cursor

### Metodo 1: DevTools (manual, mais confiavel)
1. No browser Cursor, fazer login no servico
2. Pressionar F12 (DevTools)
3. Ir em Application -> Cookies -> <dominio>
4. Localizar o cookie de sessao (JSESSIONID, ASP.NET_SessionId, etc.)
5. Copiar o Value
6. Salvar em docs/private/homelab/.env.<servico>.session

### Metodo 2: Via JavaScript na barra de URL

```text
javascript:copy(document.cookie)
```

Cole no campo de URL do browser e pressione Enter.
O clipboard tera todos os cookies da pagina.
Extrair manualmente o cookie relevante.

### Metodo 3: Via MCP Browser (quando browser esta warm)
O agente pode usar browser_navigate para um endpoint de teste
e verificar o resultado para confirmar que a sessao esta ativa.

---

## Growatt -- Endpoints Documentados

Base: <https://server.growatt.com>

| Endpoint | Metodo | Descricao |
|----------|--------|-----------|
| /indexbC.do | POST | Lista de plantas (verificacao de sessao) |
| /index/getPlantListTitle | POST | Lista detalhada de plantas |
| /panel/getDevicesByPlantList | POST | Dados do dia (date=yyyy-MM-dd, plantId=N) |
| /energy/compare/getCompareChartData | POST | Mensal/anual (type=2 mes, type=3 ano) |

Cookie necessario: JSESSIONID=<valor>

---

## Enel -- Guardrails CRITICOS

**Historico:** Em 2026-04-02, interacao com o portal Enel gerou 3 protocolos acidentais
de "Falta de Luz" (PROTO-REDACTED, PROTO-REDACTED, PROTO-REDACTED). Eles foram gerados por cliques
inadvertidos do browser-assistant em elementos de formulario.

**Regras:**
1. NUNCA navegar para paginas de registro de ocorrencias
2. NUNCA clicar em botoes de "Registrar", "Confirmar", "Enviar"
3. Ler APENAS dados de texto: valores, datas, faturas
4. Se surgir dialogo de confirmacao: CANCELAR imediatamente
5. Preferir o app Enel no celular para consultas (mais seguro)

---

## iCloud Photos -- Fluxo de Analise

```
operador: "analise fotos de nov/2022"
agente  : .\scripts\icloud-photos-fetch-range.ps1 -Start "2022-11-01" -End "2022-11-30"
agente  : Read tool em docs/private/icloud_temp/run_YYYYMMDD_HHMM/
agente  : gera insights, anota em OPERATOR_LIFE_JOURNEY_2022_2026.pt_BR.md
agente  : .\scripts\icloud-photos-fetch-range.ps1 -Cleanup
```

---

## Shorthand no Chat

| Shorthand | Acao |
|-----------|------|
| `session-collect status` | Status de todas as sessoes |
| `session-collect growatt` | Coleta Growatt (se na janela) |
| `session-collect enel` | Lembrete Enel mensal |
| `session-collect linkedin` | Checklist LinkedIn dos colaboradores |
| `session-collect social` | Checklist redes sociais do founder |
| `icloud-fetch <periodo>` | Baixar fotos de um periodo para analise |

---

## Referencias

- docs/private/homelab/ICLOUD_PHOTOS_SYNC_GUIDE.md
- docs/private/homelab/SOLAR_SYSTEM_NOTES.md
- docs/private/homelab/ENEL_ACCOUNT_NOTES.md
- docs/private/commercial/candidates/linkedin_peer_review/ (ATS dos colaboradores)
- .cursor/skills/candidate-ats-evaluation/SKILL.md (Passo 4 -- LinkedIn ao vivo)

## Skill versao 1.0 - 2026-04-03
