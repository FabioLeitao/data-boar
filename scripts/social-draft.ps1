<#
.SYNOPSIS
    Gera rascunhos de posts para social media baseados em contexto do repositorio.
    Token-aware: le apenas o que precisa, gera texto minimo viavel.

.DESCRIPTION
    Modos:
    - milestone: celebra uma feature/release do Data Boar
    - rca: estrutura um RCA blameless
    - study: update de estudo/certificacao
    - labop: "esta semana no lab-op"
    - lgpd: conteudo sobre compliance/LGPD
    - wordpress: gera estrutura de post para blog

.PARAMETER Mode
    Tipo de post (milestone|rca|study|labop|lgpd|wordpress)

.PARAMETER Title
    Titulo ou tema do post

.PARAMETER Network
    Rede alvo (linkedin|x|both|blog)

.PARAMETER Output
    Caminho de saida do rascunho (default: docs/private/social_drafts/)

.EXAMPLE
    .\scripts\social-draft.ps1 -Mode milestone -Title "OCR detection implementado" -Network linkedin
    .\scripts\social-draft.ps1 -Mode rca -Title "Bug PDF encoding edge case" -Network both
#>
param(
    [Parameter(Mandatory)]
    [ValidateSet("milestone","rca","study","labop","lgpd","wordpress")]
    [string]$Mode,

    [Parameter(Mandatory)]
    [string]$Title,

    [ValidateSet("linkedin","x","both","blog")]
    [string]$Network = "both",

    [string]$Output = "docs\private\social_drafts"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path $PSScriptRoot -Parent

# Garante pasta de saida
$outDir = Join-Path $repo $Output
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$date = Get-Date -Format "yyyy-MM-dd"
$slug = ($Title -replace '[^a-zA-Z0-9]','-').ToLower() -replace '-+','-'
$slug = $slug.Trim('-').Substring(0, [Math]::Min($slug.Length,40))

function Get-LinkedInTemplate {
    param($mode, $title)
    switch ($mode) {
        "milestone" {
@"
🚀 **$title**

[1-2 linhas sobre O QUE foi implementado e POR QUE importa para compliance]

O que isso resolve na pratica:
→ [beneficio 1]
→ [beneficio 2]
→ [beneficio 3]

Stack usado: [tecnologias]

O Data Boar continua evoluindo. Zero regressoes nesta rodada. ✅

#DataBoar #LGPD #GDPR #Python #SRE #DataProtection
---
[Variante curta para X (280 chars max):]
🚀 $title — Data Boar. [frase impacto]. Zero regressoes. #DataBoar #LGPD 🔗 [link]
"@
        }
        "rca" {
@"
📝 **Post-mortem blameless: $title**

Blameless porque: erros acontecem. O que importa e o que aprendemos.

**O que aconteceu:**
[descricao tecnica neutra, sem culpar pessoas]

**Impacto:**
[o que foi afetado, por quanto tempo]

**Root Cause:**
[causa raiz identificada]

**O que corrigimos:**
→ [acao 1]
→ [acao 2]

**O que garantimos para nao repetir:**
→ [teste adicionado]
→ [automacao criada]
→ [regra/guardrail novo]

Cada bug e uma oportunidade de fazer o codigo mais resiliente.
Lesson learned. Ship it. 🚢

#SRE #BlamelessCulture #DataBoar #Engineering
"@
        }
        "study" {
@"
📚 **$title**

[O que completei / o que estou estudando agora]

3 coisas que aprendi:
1. [insight 1]
2. [insight 2]
3. [insight 3]

[Como isso se conecta com o que faco no dia a dia]

Se voce esta na mesma trilha: [recurso ou dica]

#CWL #Cybersecurity #LGPD #Learning #PUCRio
"@
        }
        "labop" {
@"
🖥️ **Esta semana no lab-op: $title**

[Contexto: o que estava tentando resolver]

O que fiz:
→ [acao 1]
→ [acao 2]

O que funcionou: [✅]
O que nao funcionou (ainda): [🔧]

Proximo passo: [o que vem a seguir]

Documentado em: [ADR/PLAN se relevante]

#HomeLabOps #SRE #Docker #Ansible #DataBoar
"@
        }
        "lgpd" {
@"
⚖️ **$title**

[Contexto: qual obrigacao LGPD/GDPR esta em jogo]

O que a lei diz (simplificado):
→ [artigo/obrigacao em linguagem acessivel]

O que as empresas costumam errar:
→ [erro 1]
→ [erro 2]

O que fazer na pratica:
→ [acao 1]
→ [acao 2]

[Referencia ao Data Boar se relevante]

DPO ou gestor: salve este post para a proxima auditoria. 📌

#LGPD #GDPR #Compliance #PrivacidadeDeDados #DataProtection
"@
        }
        "wordpress" {
@"
# $title

**Meta description (155 chars):**
[descricao para SEO]

**Keywords:**
[palavra-chave 1], [palavra-chave 2], [palavra-chave 3]

---

## Introducao (150-250 palavras)
[Problema que este post resolve. Por que o leitor deve continuar.]

## [Secao principal 1]
[Conteudo tecnico com exemplos]

## [Secao principal 2]
[Continuacao]

## Conclusao
[Resumo dos pontos principais e call-to-action]

---
**Tags:** #DataBoar #LGPD #SRE
**Categoria sugerida:** [compliance|sre|product|labop]
**Tempo de leitura estimado:** [X min]
**Crosspost:** LinkedIn (resumo) + X (thread)
"@
        }
    }
}

# Gera rascunho LinkedIn
if ($Network -in @("linkedin","both")) {
    $content = Get-LinkedInTemplate -mode $Mode -title $Title
    $outFile = Join-Path $outDir "${date}_linkedin_${Mode}_${slug}.md"
    Set-Content -Path $outFile -Value $content -Encoding UTF8
    Write-Host "✅ LinkedIn draft: $outFile"
}

# Para X: versao curta
if ($Network -in @("x","both")) {
    $xContent = @"
# X/Twitter — Rascunho: $Title ($date)

**Thread principal (tweet 1/N):**
[Gancho impactante em 1 frase — max 240 chars]

**Tweet 2:**
[Contexto ou detalhe]

**Tweet 3:**
[Evidencia ou resultado]

**Tweet final:**
[CTA + link + hashtags]
#DataBoar #LGPD #SRE
"@
    $xFile = Join-Path $outDir "${date}_x_${Mode}_${slug}.md"
    Set-Content -Path $xFile -Value $xContent -Encoding UTF8
    Write-Host "✅ X draft: $xFile"
}

# Para blog/WordPress
if ($Network -eq "blog") {
    $content = Get-LinkedInTemplate -mode "wordpress" -title $Title
    $outFile = Join-Path $outDir "${date}_blog_${Mode}_${slug}.md"
    Set-Content -Path $outFile -Value $content -Encoding UTF8
    Write-Host "✅ Blog draft: $outFile"
}

Write-Host ""
Write-Host "Rascunhos em: $outDir"
Write-Host "Proximos passos:"
Write-Host "  1. Edite os placeholders [...] com conteudo real"
Write-Host "  2. Revise tom e tamanho"
Write-Host "  3. Para LinkedIn: copie e cole direto no editor de posts"
Write-Host "  4. Para X: use cada tweet separado (280 chars max por tweet)"
