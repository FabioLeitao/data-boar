#Requires -Version 5.1
<#
.SYNOPSIS
    Financas Domesticas -- Dashboard e coleta READ-ONLY de todas as contas e utilidades.
.DESCRIPTION
    Agrega Enel, Aguas de Niteroi, Claro, Leste Telecom, Growatt (solar) e Caixa.
    Modos: status | dashboard | enel | aguas | claro | leste | growatt | update | capex | opex | health
.NOTES
    GUARDRAIL GLOBAL: READ-ONLY. Nao alterar servicos sem confirmacao do operador.
    Versao: 1.0 | Criado: 2026-04-03
#>
param(
    [ValidateSet("status","dashboard","enel","aguas","claro","leste","growatt","update","capex","opex","health","shopping")]
    [string]$Mode = "status"
)
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$scripts  = $PSScriptRoot
function Write-Header($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Info($m)   { Write-Host "  ... $m"   -ForegroundColor Gray }
function Write-Guard($m)  { Write-Host " SAFE $m"   -ForegroundColor Magenta }
function Write-Money($l,$v) { Write-Host ("  {0,-28} R$ {1,10}" -f $l,$v) -ForegroundColor Yellow }
Write-Guard "READ-ONLY GLOBAL -- Nenhum servico sera alterado"
switch ($Mode) {
    { $_ -in "status","dashboard" } {
        Write-Header "Dashboard Financeiro Domestico -- $((Get-Date -Format 'yyyy-MM-dd'))"
        Write-Host "`n--- FIXOS MENSAIS ---" -ForegroundColor White
        Write-Money "Financiamento Caixa"      "2.585,29"
        Write-Money "Energia Enel UC8092489"   "? (coletar)"
        Write-Money "Agua Aguas de Niteroi"    "? (coletar)"
        Write-Money "Celular Claro"             "? (coletar)"
        Write-Money "Internet Leste Telecom"    "? (coletar)"
        Write-Host "`n--- OFFSET SOLAR (Growatt) ---" -ForegroundColor White
        Write-Info "Geracao solar: coletar via growatt-session-collect.ps1 -Mode month"
        Write-Host "`n--- SAUDE ---" -ForegroundColor White
        Write-Info "Plano Sulamerica (employer plan, until 2025) | InComm Payments (2026+, confirmar)"
        Write-Info "Suplementos: ver docs/private/"
        Write-Host "`n--- PARA PREENCHER OS ? ---" -ForegroundColor White
        Write-Info ".\scripts\household-finance.ps1 -Mode update"
    }
    "enel"    { & (Join-Path $scripts "enel-session-collect.ps1") }
    "aguas"   { & (Join-Path $scripts "aguas.ps1") }
    "claro"   { & (Join-Path $scripts "claro.ps1") }
    "leste"   { & (Join-Path $scripts "leste.ps1") }
    "growatt" { & (Join-Path $scripts "growatt-session-collect.ps1") -Mode month }
    "update" {
        Write-Header "Coletando todas as contas..."
        Write-Guard "Apenas leitura."
        foreach ($svc in @("enel","aguas","claro","leste","growatt")) {
            Write-Info ">>> $svc"
            & (Join-Path $PSScriptRoot "household-finance.ps1") -Mode $svc
        }
        Write-Info "Concluido. Veja instrucoes acima para coleta manual onde necessario."
    }
    "opex" {
        Write-Header "OPEX -- Custos Mensais Estimados"
        Write-Money "Financiamento Caixa"   "2.585,29"; Write-Info "  (193 meses restantes pos-FGTS jul/2025)"
        Write-Money "Energia Eletrica"       "? (Enel UC8092489)"
        Write-Money "Agua/Esgoto"            "? (Aguas de Niteroi)"
        Write-Money "Internet"               "? (Leste Telecom)"
        Write-Money "Celular"                "? (Claro)"
        Write-Money "Plano de Saude"         "? (InComm Payments 2026)"
        Write-Money "Suplementos est."       "50-150"
        Write-Money "Offset solar"           "-? (Growatt)"
        Write-Info "Rode -Mode update para preencher os campos '?'"
    }
    "capex" {
        Write-Header "CAPEX -- Investimentos em Infraestrutura"
        Write-Info "Servidor Dell (homelab principal): pre-jun/2025"
        Write-Info "Monitor Dell: confirmado jun/2025"
        Write-Info "Equipamentos UniFi (UDM + switches): em producao"
        Write-Info "Paineis solares + inversor Growatt: gerando energia"
        Write-Info "Hardware de rede catalogado: set/2025"
        Write-Info "Detalhe: docs/private/homelab/HARDWARE_CATALOG.md"
    }
    "health" {
        Write-Header "Saude -- Medicacoes e Historico"
        Write-Host "`n--- CONFIRMADAS (fotos iCloud) ---" -ForegroundColor Green
        Write-Info "Suplementos: ver docs/private/"
        Write-Info "  Comum em burnout + home office. ~R$ 30-80/mes."
        Write-Host "`n--- A CONFIRMAR (Signal photos jun/2025 bloqueados) ---" -ForegroundColor Yellow
        Write-Info "Fotos com prescricoes: ver docs/private/"
        Write-Info "  Para acessar: abrir iCloud for Windows, entao:"
        Write-Info "  .\scripts\icloud-photos-fetch-range.ps1 -Start 2025-06-01 -End 2025-06-30"
        Write-Info "Suplementos e medicacoes: ver docs/private/"
        Write-Host "`n--- HISTORICO DE COMPRAS FARMACIA ---" -ForegroundColor White
        Write-Info "Historico de farmacia: ver docs/private/"
        Write-Info "  Verificar docs/private/ para detalhes"
        Write-Host "`n--- CONSULTAS DOCUMENTADAS ---" -ForegroundColor White
        Write-Info "05/jun/2025: Medico assistente (ver docs/private/)"
        Write-Info "  CID e periodo de afastamento: ver docs/private/"
        Write-Info "22/set/2025: Consulta medica: ver docs/private/"
        Write-Host "`n--- PLANO DE SAUDE ---" -ForegroundColor White
        Write-Info "2022-2025: Sulamerica Especial 100 (employer plan)"
        Write-Info "2026+:     Confirmar InComm Payments"
    }

    "shopping" {
        Write-Header "Lista de Compras e CAPEX"
        $listFile = Join-Path $repoRoot "docs\private\homelab\SHOPPING_LIST_CAPEX.md"
        if (Test-Path $listFile) {
            Get-Content $listFile
            Write-Info "Arquivo completo: $listFile"
        } else {
            Write-Info "Lista nao encontrada. Execute: New-Item $listFile"
        }
    }
}

