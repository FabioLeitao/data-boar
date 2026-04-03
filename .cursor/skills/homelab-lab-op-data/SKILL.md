# Skill: homelab-lab-op-data

## When to use

When the operator asks to collect, refresh, or report on any LAB-OP system data:
- Solar/Growatt: dados de geracao, kWh, inversor, datalogger, historico
- Enel: faturas, consumo, status de conta, falta de luz
- UDM: scan de rede, clientes, VLANs, alertas, configuracoes
- Correlacao energetica: solar gerado vs grid consumido por mes
- Inventario de hosts: software, hardware, versions por maquina

## Read first

1. `.cursor/rules/lab-op-systems-context.mdc` -- sistema registry + guardrails criticos
2. `docs/private/homelab/OPERATOR_RETEACH.md` (B1-B6)
3. Arquivo especifico do sistema na secao 2 da regra

## Workflow por tarefa

### Solar / Growatt

**Dados rapidos (ja capturados):**
- Ler `docs/private/homelab/SOLAR_SYSTEM_NOTES.md` -- snapshot 2026-04-02
- Contem: Plant 843372, Inverter MIC 3000TL-X S/N DRH3B140SQ, 25,844 kWh total
- Se dados < 7 dias e o operador nao pediu "ao vivo" -> usar o arquivo, nao re-navegar

**Dados novos (ao vivo):**
1. Verificar se `.\scripts\growatt.ps1 -Mode api` esta configurado (requer token ShinePhone)
2. Se token disponivel: `.\scripts\growatt.ps1 -Mode api -Out docs/private/homelab/SOLAR_SYSTEM_NOTES.md`
3. Se nao: navegar browser para `https://server.growatt.com` (operador ja deve estar autenticado)
   - Extrair dados do dashboard (nao usar URL direta -- SPA)
   - Atualizar `SOLAR_SYSTEM_NOTES.md` com novos valores
4. Nunca fazer login automatico (sem credenciais no codigo)

**Endpoints conhecidos (autenticacao por cookie de sessao):**

```
POST /panel/tlx/getTLXTotalData?plantId=843372      -- total + hoje kWh
POST /panel/tlx/getTLXEnergyDayChart                -- grafico do dia
POST /panel/getPlantData?plantId=843372             -- dados da planta
GET  /panel/alertPlantEvent?plantId=843372          -- alertas
```

### Enel / Grid

**REGRA DE OURO: NAO USAR O BROWSER ENEL**
- Overlay do portal gera protocolos de "Falta de Luz" acidentalmente
- Tres protocolos ja criados acidentalmente (PROTO-REDACTED, PROTO-REDACTED, PROTO-REDACTED)

**Dados disponiveis (ja capturados):**
- `docs/private/homelab/ENEL_ACCOUNT_NOTES.md` tem:
  - UC: 8092489 (Niteroi)
  - 10 faturas (pag 1/6), referencias de Jun/2025 a Mar/2026
  - Total debitos: R$ 0,00 (conta em dia em 2026-04-02)

**Para novos dados:**
- Executar: `.\scripts\enel.ps1` (le arquivo, nao browser)
- Para historico: pedir ao operador para baixar CSV/PDF do portal manualmente
- Para grafico de consumo: operador navega, digita CPF, faz screenshot, passa para o AI

**Nao fazer nunca:**
- Clicar em qualquer elemento da pagina Enel sem snapshot fresco
- Preencher CPF, CNPJ, senha ou dados pessoais no browser
- Assumir que clique funcionou sem verificar snapshot apos acao

### UDM / Rede

**Verificar se ha scan recente:**

```powershell
Get-ChildItem docs/private/homelab/reports/udm_api_*.json | Sort LastWriteTime -Desc | Select -First 1
```

**Se scan fresco (< 3 dias) e query basica:** ler o arquivo JSON, nao re-probar.

**Para novo scan:**

```powershell
# Com Bitwarden (recomendado):
$env:BW_SESSION = (bw unlock --raw)
.\scripts\udm.ps1 -Command scan -Out "docs/private/homelab/reports/udm_api_$(Get-Date -Format yyyyMMdd_HHmmss).json"

# Com API key direta (temporario):
.\scripts\udm.ps1 -Command clients -ApiKey $env:LAB_UDM_API_KEY
```

**Comandos disponiveis:**
- `status` -- versao, site, uptime
- `clients` -- lista de dispositivos conectados (IP, MAC, hostname, SSID)
- `wifi` -- configuracoes de redes Wi-Fi
- `vlans` -- VLANs e subredes
- `alerts` -- alertas ativos
- `ports` -- portas do switch integrado UDM-SE
- `scan` -- tudo acima de uma vez

### Correlacao Solar x Grid (energy-report)

1. Ler `SOLAR_SYSTEM_NOTES.md` -> extrair kWh gerado por mes (se disponivel)
2. Ler `ENEL_ACCOUNT_NOTES.md` -> extrair kWh consumido por mes (se disponivel)
3. Executar: `.\scripts\energy-report.ps1`
4. Output esperado: tabela mes a mes com geracao, consumo, saldo, % auto-suficiencia

**Limitacao atual:** kWh mensais da Enel nao estao capturados (apenas IDs de faturas).
Para obter: operador baixa o "Grafico de Consumo" do portal Enel manualmente.

## Criacao de relatório completo (lab-op-data-report)

Quando o operador pede "relatorio completo do lab":

```powershell
# 1. Inventario de hosts (SSH)
.\scripts\lab-op.ps1 -Action report-all

# 2. Scan UDM
.\scripts\udm.ps1 -Command scan -Out "docs/private/homelab/reports/udm_api_$(Get-Date -Format yyyyMMdd).json"

# 3. Solar status
.\scripts\growatt.ps1

# 4. Enel status
.\scripts\enel.ps1

# 5. Energy correlation
.\scripts\energy-report.ps1
```

## Arquivos que podem ser atualizados por esta skill

- `docs/private/homelab/SOLAR_SYSTEM_NOTES.md` -- dados Growatt (nunca commitar)
- `docs/private/homelab/ENEL_ACCOUNT_NOTES.md` -- dados Enel (nunca commitar)
- `docs/private/homelab/reports/*.json` -- snapshots UDM (nunca commitar)
- `docs/private/homelab/OPERATOR_RETEACH.md` -- facts atualizados (nunca commitar)

## Guardrails finais

- NUNCA preencher CPF/CNPJ/senha/token no browser
- NUNCA commitar arquivos de `docs/private/homelab/` para Git
- NUNCA colar IPs, MACs, numeros de UC, S/N de hardware em arquivos rastreados
- NUNCA executar scans em loop (um scan por necessidade, salvar em arquivo)
- SEMPRE preferir ler arquivos existentes antes de fazer nova coleta
- SEMPRE confirmar elemento refs antes de clicar no portal Enel (risco de protocolo acidental)

See also: `.cursor/rules/lab-op-systems-context.mdc` (registry conciso + guardrails).

