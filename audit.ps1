# AUDIT RITUAL - DATA BOAR INTEGRITY ENGINEERING
$logDir = "$PSScriptRoot\logs"
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

$logFile = "$logDir\audit-$(Get-Date -Format 'yyyyMMdd_HHmm').log"
$sessionLink = "$logDir\latest.log"

# O Envelope de Auditoria
"--- AUDIT START: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ---" | Tee-Object -FilePath $logFile
"Operator: $($env:USERNAME)" | Tee-Object -FilePath $logFile -Append
"Branch: $(git rev-parse --abbrev-ref HEAD) | Commit: $(git rev-parse --short HEAD)" | Tee-Object -FilePath $logFile -Append
"---------------------------------------------------" | Tee-Object -FilePath $logFile -Append

# Execução do Gate com captura total
.\scripts\check-all.ps1 2>&1 | Tee-Object -FilePath $logFile -Append

"---------------------------------------------------" | Tee-Object -FilePath $logFile -Append
"--- AUDIT END: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ---" | Tee-Object -FilePath $logFile -Append

# Cria um link simbólico (ou copia) para o log mais recente para fácil acesso
Copy-Item $logFile $sessionLink -Force
