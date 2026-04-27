#requires -Version 5.1
# scripts/dependabot-osv-reconcile.ps1
#
# Windows / pwsh twin of scripts/dependabot-osv-reconcile.sh.
# When the Cloud Agent's gh integration token returns 403 on
# /repos/.../dependabot/alerts/<n> but the operator can read the alert
# in the GitHub web UI, this wrapper queries OSV.dev for a parser-grade
# verdict instead of falling back to "raw string heuristic" guesses.
#
# Doctrine: docs/ops/inspirations/THE_ART_OF_THE_FALLBACK.md section 2,
# docs/ops/inspirations/SUPPLY_Colleague-NN_AND_TRUST_SIGNALS.md.
#
# Usage:
#   .\scripts\dependabot-osv-reconcile.ps1 -Ecosystem crates.io -Package pyo3 -Version 0.23.5
#   .\scripts\dependabot-osv-reconcile.ps1 -Ecosystem PyPI -Package cryptography -Version 46.0.7

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Ecosystem,

    [Parameter(Mandatory = $true)]
    [string]$Package,

    [Parameter(Mandatory = $true)]
    [string]$Version
)

$ErrorActionPreference = 'Stop'

$body = @{
    package = @{ name = $Package; ecosystem = $Ecosystem }
    version = $Version
} | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod `
        -Method Post `
        -Uri 'https://api.osv.dev/v1/query' `
        -ContentType 'application/json' `
        -Body $body `
        -TimeoutSec 15
}
catch {
    Write-Error "OSV.dev query failed: $($_.Exception.Message)"
    Write-Error 'Doctrine: surface the failure, never silently downgrade.'
    exit 3
}

if ($null -eq $response.vulns -or $response.vulns.Count -eq 0) {
    Write-Host "[OK] No advisories on OSV.dev for ${Ecosystem}:${Package}@${Version}."
    Write-Host '[OK] If the operator sees a Dependabot alert at'
    Write-Host '     /security/dependabot/<n> for this package, it may be a'
    Write-Host '     newer/internal advisory - ask the operator to paste the'
    Write-Host '     CVE / GHSA / RUSTSEC id and re-trigger.'
    exit 0
}

Write-Host "[FOUND] $($response.vulns.Count) advisory(ies) for ${Ecosystem}:${Package}@${Version}:"
foreach ($v in $response.vulns) {
    $severity = if ($v.database_specific.severity) { $v.database_specific.severity } else { 'n/a' }
    $fixed = 'n/a'
    foreach ($a in @($v.affected)) {
        foreach ($r in @($a.ranges)) {
            foreach ($e in @($r.events)) {
                if ($e.PSObject.Properties['fixed']) { $fixed = $e.fixed }
            }
        }
    }
    $url = 'n/a'
    foreach ($ref in @($v.references)) {
        if ($ref.type -in @('ADVISORY', 'WEB')) { $url = $ref.url; break }
    }

    Write-Host ("  - {0} | {1} | {2}" -f $v.id, $severity, $v.summary)
    Write-Host ("      fixed: {0}" -f $fixed)
    Write-Host ("      url:   {0}" -f $url)
}
