<#
.SYNOPSIS
    Abre perfis LinkedIn de candidatos no browser em lote ou individualmente.
    Quando o Cursor tiver browser autenticado, use junto com o agente de IA
    para enriquecer os arquivos ATS com dados ao vivo.

.PARAMETER Names
    Lista de apelidos de candidatos (separados por virgula). Padrao: todos.

.PARAMETER Delay
    Delay em segundos entre abertura de cada perfil. Padrao: 3.

.PARAMETER Top
    Abrir apenas os N primeiros da lista.

.EXAMPLE
    # Abrir perfil de Contributor-A:
    .\scripts\linkedin-review-batch.ps1 -Names "contributor-a"

    # Abrir top 5 candidatos prioritarios:
    .\scripts\linkedin-review-batch.ps1 -Top 5

    # Abrir todos (com delay de 5s):
    .\scripts\linkedin-review-batch.ps1 -Delay 5
#>

param(
    [string]$Names = "",
    [int]$Delay = 3,
    [int]$Top = 0
)

# Mapa completo de slugs LinkedIn por apelido
$pool = [ordered]@{
    "contributor-a"         = "contributor-a"
    "pedro"        = "pedro-Colleague-F-alto%C3%A9-0a360a227"
    "colleague-h"   = "colleague-h"
    "andreColleague-I"   = "colleague-i"
    "aca"          = "antonio-carlos-azevedo-08328b9"
    "braga"        = "Colleague-Q--braga-"
    "caterine"     = "caterine-pastorino-017538350"
    "Colleague-J"     = "rebeloc"
    "Colleague-S"          = "Colleague-R"
    "Colleague-C"       = "felippe-ferr%C3%A3o-343b0328"
    "freire"       = "Colleague-Q-freire-66875242"
    "freitas"      = "luis-freitas-5ab2702a"
    "Colleague-P"       = "Colleague-OColleague-P"
    "irlan"        = "irlan-sales-3871b076"
    "madruga"      = "marcelo-madruga"
    "marcos"       = "marcos-rocha-dba"
    "Colleague-D"      = "Colleague-D-leit%C3%A3o-53600089"
    "Colleague-T"      = "Colleague-Trestier"
    "Colleague-K"          = "pColleague-L"
    "Colleague-Ugomez"  = "ravigomez"
    "Colleague-UColleague-V"  = "Colleague-U-c-Colleague-V"
    "ramon"        = "ramon-oliveira-bb2317a3"
    "colleague-a"       = "colleague-a-mmoreira"
    "wagner"       = "waferreira"
}

# Filtrar candidatos
$selected = if ($Names) {
    $nameList = $Names -split "," | ForEach-Object { $_.Trim().ToLower() }
    $pool.GetEnumerator() | Where-Object { $_.Key -in $nameList }
} else {
    $pool.GetEnumerator()
}

if ($Top -gt 0) { $selected = $selected | Select-Object -First $Top }

Write-Host "Abrindo $(@($selected).Count) perfis LinkedIn..." -ForegroundColor Cyan
Write-Host "Delay entre perfis: ${Delay}s" -ForegroundColor Gray
Write-Host ""
Write-Host "INSTRUCAO PARA O AGENTE:" -ForegroundColor Yellow
Write-Host "  Apos abrir os perfis, use no Cursor:" -ForegroundColor Yellow
Write-Host "  'Revise o LinkedIn de [nome] e atualize o ATS com os dados ao vivo'" -ForegroundColor Yellow
Write-Host ""

$i = 0
foreach ($entry in $selected) {
    $i++
    $url = "https://www.example.com/profile/redacted)"
    Write-Host "[$i/$(@($selected).Count)] Abrindo: $($entry.Key) -> $url"
    Start-Process $url
    if ($i -lt @($selected).Count) { Start-Sleep -Seconds $Delay }
}

Write-Host ""
Write-Host "Concluido. $i perfis abertos no browser." -ForegroundColor Green
Write-Host "Dica: Use 'ats show [nome]' para ver o ATS atual de cada candidato." -ForegroundColor Cyan
