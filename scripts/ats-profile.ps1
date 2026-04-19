# =============================================================================
# ATS / Pool de Talentos -- atalhos globais (adicionar ao $PROFILE do PowerShell)
# =============================================================================
# Adicione ao seu perfil PowerShell:
#   code $PROFILE   (ou notepad $PROFILE)
#   . "C:\Users\<username>\Documents\dev\data-boar\scripts\ats-profile.ps1"
# Ou inclua direto com:
#   Add-Content $PROFILE '. "C:\path\to\scripts\ats-profile.ps1"'
# =============================================================================

$AtsRepoRoot = "C:\Users\<username>\Documents\dev\data-boar"
$AtsScript   = "$AtsRepoRoot\scripts\ats.ps1"
$UdmScript   = "$AtsRepoRoot\scripts\udm.ps1"

# --- Funcao principal: ats ---
function ats {
    param(
        [Parameter(Position=0)] [string]$Command = "help",
        [Parameter(Position=1)] [string]$Arg1 = "",
        [Parameter(Position=2)] [string]$Arg2 = "",
        [switch]$Force,
        [switch]$JsonOnly
    )
    $args2 = @($Command)
    if ($Arg1)    { $args2 += $Arg1 }
    if ($Arg2)    { $args2 += $Arg2 }
    if ($Force)   { $args2 += "-Force" }
    if ($JsonOnly){ $args2 += "-JsonOnly" }
    powershell -ExecutionPolicy Bypass -File $AtsScript @args2
}

# --- Funcao UDM ---
function udm {
    param(
        [Parameter(Position=0)] [string]$Command = "status",
        [string]$ApiKey = ""
    )
    $args2 = @($Command)
    if ($ApiKey) { $args2 += "-ApiKey"; $args2 += $ApiKey }
    powershell -ExecutionPolicy Bypass -File $UdmScript @args2
}

# --- Atalhos curtissimos ---
function ats-import    { ats import $args[0] }
function ats-scan      { ats scan $args[0] }
function ats-list      { ats list }
function ats-show      { ats show $args[0] }
function pool          { ats list }                    # alias: pool
function udm-scan      { udm scan }
function udm-clients   { udm clients }
function udm-wifi      { udm wifi }

# --- Funcao de ajuda rapida ---
function ats-help {
    Write-Host @"
Atalhos ATS disponiveis:

  ats import <pdf>    Importar PDF de candidato
  ats import-all      Importar todos PDFs novos
  ats scan <nome>     Extrair dados de PDF (JSON)
  ats list / pool     Listar todos os candidatos
  ats show <nome>     Ver ATS de um candidato
  ats linkedin <slug> Abrir LinkedIn no browser
  ats udm             Status do UDM
  ats udm-scan        Scan completo da rede UDM
  udm-clients         Lista clientes conectados na rede
  udm-wifi            Lista redes Wi-Fi
"@ -ForegroundColor Cyan
}

Write-Host "[ATS+UDM] Atalhos carregados. Digite 'ats-help' para ver os comandos." -ForegroundColor DarkCyan
