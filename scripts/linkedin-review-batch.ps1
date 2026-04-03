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
    # Abrir perfil de Ivan:
    .\scripts\linkedin-review-batch.ps1 -Names "ivan"

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
    "ivan"         = "ivanfilho"
    "pedro"        = "pedro-herminio-alto%C3%A9-0a360a227"
    "andreeudes"   = "andreeudes"
    "andrelucas"   = "andreplucas"
    "aca"          = "antonio-carlos-azevedo-08328b9"
    "braga"        = "rodrigo--braga-"
    "caterine"     = "caterine-pastorino-017538350"
    "clebinho"     = "rebeloc"
    "ebo"          = "eliezio"
    "ferrao"       = "felippe-ferr%C3%A3o-343b0328"
    "freire"       = "rodrigo-freire-66875242"
    "freitas"      = "luis-freitas-5ab2702a"
    "gondim"       = "ricardogondim"
    "irlan"        = "irlan-sales-3871b076"
    "madruga"      = "marcelo-madruga"
    "marcos"       = "marcos-rocha-dba"
    "marluce"      = "marluce-leit%C3%A3o-53600089"
    "murillo"      = "murillorestier"
    "pim"          = "pwaaijenberg"
    "rafaelgomez"  = "ravigomez"
    "rafaelsilva"  = "rafael-c-silva"
    "ramon"        = "ramon-oliveira-bb2317a3"
    "talita"       = "talita-mmoreira"
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
    $url = "https://www.linkedin.com/in/$($entry.Value)"
    Write-Host "[$i/$(@($selected).Count)] Abrindo: $($entry.Key) -> $url"
    Start-Process $url
    if ($i -lt @($selected).Count) { Start-Sleep -Seconds $Delay }
}

Write-Host ""
Write-Host "Concluido. $i perfis abertos no browser." -ForegroundColor Green
Write-Host "Dica: Use 'ats show [nome]' para ver o ATS atual de cada candidato." -ForegroundColor Cyan
