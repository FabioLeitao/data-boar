param(
    [Parameter(Mandatory = $true)]
    [string]$SnapshotPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $SnapshotPath)) {
    throw "Snapshot file not found: $SnapshotPath"
}

$content = Get-Content -LiteralPath $SnapshotPath -Raw -Encoding UTF8

# Target only the mojibake patterns we have seen so far.
$replacements = @(
    @("Andr� Lucas", "André Lucas"),
    @("Ferr�o", "Ferrão"),
    @("Re-run de pool sync apos", "Re-run de pool sync após"),
    @("Re-run de pool sync apos", "Re-run de pool sync após"),
    @("automa��o", "automaçao"),
    @("automacao", "automaçao"),
    @("automacao", "automaçao")
)

foreach ($r in $replacements) {
    $content = $content -replace [regex]::Escape($r[0]), $r[1]
}

Set-Content -LiteralPath $SnapshotPath -Value $content -Encoding UTF8

Write-Host "Normalized: $SnapshotPath"

