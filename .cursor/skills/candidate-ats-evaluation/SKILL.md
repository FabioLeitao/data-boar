# Skill: candidate-ats-evaluation

**Proposito:** Importar PDF de perfil LinkedIn/CV, extrair dados estruturados,
gerar ou atualizar arquivo ATS individual, e (quando autenticado) visitar perfis ao vivo.

**Quando usar:**
- Um novo PDF de candidato foi adicionado em `docs/private/team_info/`
- Operador quer importar ou atualizar ATS de um candidato especifico
- Sessao tem autenticacao LinkedIn ativa no browser Cursor (aproveitamento maximo)
- Exploracao de redes sociais complementares (X, GitHub, Gravatar, etc.)

---

## Wrapper CLI (USE PRIMEIRO - economiza tokens)

```powershell
# LISTA todos os candidatos
.\scripts\talent.ps1 list

# ESCANEIA PDFs novos
.\scripts\talent.ps1 scan

# IMPORTA PDF novo (aceita nome parcial - busca em docs/private/team_info/)
.\scripts\talent.ps1 import "Sample_Candidate.pdf"
.\scripts\talent.ps1 import "Linked in Profile - Candidate 2026.pdf"

# ABRE ATS de um candidato no editor (aceita apelido do pool)
.\scripts\talent.ps1 review candidate_a
.\scripts\talent.ps1 review candidate_b
.\scripts\talent.ps1 review candidate_c

# ABRE LinkedIn no browser
.\scripts\talent.ps1 linkedin candidate_a
.\scripts\talent.ps1 linkedin candidate_b

# BUSCA keyword em todos os ATS
.\scripts\talent.ps1 search "LGPD"
.\scripts\talent.ps1 search "CTO"
.\scripts\talent.ps1 search "Open to Work"

# EXTRAI JSON estruturado do PDF
.\scripts\talent.ps1 extract "Sample_Candidate.pdf"
```

---

## Workflow (siga nesta ordem)

### Passo 1 — Deteccao de novos PDFs

```powershell
.\scripts\talent.ps1 scan
```

### Passo 2 — Extracao automatica (sem IA)

```powershell
# Para um PDF especifico:
.\scripts\talent.ps1 import "Linked in Profile - <NOME>.pdf"

# Para processar todos de uma vez (batch):
Get-ChildItem "docs\private\team_info\" -Filter "*.pdf" | ForEach-Object {
    uv run --with pypdf python scripts/extract_cv_pdf.py "$($_.FullName)" --json
}
```

### Passo 3 — Verificar e enriquecer ATS (leve, sem browser)

```powershell
# Abrir o arquivo gerado no editor:
.\scripts\talent.ps1 review <apelido>
```

### Passo 4 — Visitar LinkedIn ao vivo (requer autenticacao no browser Cursor)

Quando o operador esta autenticado no LinkedIn pelo browser Cursor, usar o browser para:
1. Navegar ao perfil: `browser_navigate(url: Candidates[$key].LinkedIn)`
2. Extrair via snapshot acessibilidade:
   - Headline atual, empresa atual, localizacao
   - Open to Work (se ativo, buscar no snapshot por "Buscando emprego")
   - Seguidores (buscar "seguidores" no snapshot)
   - Posts/certificacoes recentes (secao "Atividades")
   - Conexoes em comum
3. Atualizar ATS individual com dados ao vivo

**Dados chave a buscar no LinkedIn snapshot:**

```
- Headline: link com nome completo contem o headline
- Open to Work: listitem com "Buscando emprego" + lista de cargos
- Seguidores: "N.NNN seguidores"
- Empresa: button com nome da empresa
- Conexoes: "N conexoes" ou "Mais de 500 conexoes"
- Conexoes em comum: "Nome, Nome e mais N conexoes em comum"
- Posts recentes: listitems com data relativa (2 sem, 1 m, etc.)
```

### Passo 5 — Redes sociais complementares

**LinkedIn:** Principal - coberto pelo workflow acima.

**X/Twitter:** Buscar no ATS ou PDF por "@" handles. Visitar <https://x.com/HANDLE> se encontrado.

**GitHub:** Para perfis tecnicos (SWE, DevOps), buscar por nome no GitHub:

```
https://github.com/<nome-normalizado>
https://api.github.com/search/users?q=<nome>
```

**Gravatar:** Baseado no email extraido do PDF:

```
https://www.gravatar.com/<md5-do-email>
```

**YouTube:** Buscar por nome completo se o candidato cria conteudo.

**Google Search rapido:**

```
"Nome Completo" site:linkedin.com OR site:github.com OR site:twitter.com
```

---

## Estrutura de arquivos

```
docs/private/team_info/                              # PDFs fonte (gitignored)
  Linked in Profile - <Nome> 2026.pdf

docs/private/commercial/candidates/linkedin_peer_review/
  POOL_INDEX.pt_BR.md                               # Indice central com emails e URLs
  individual/
    CANDIDATE_A_ATS.pt_BR.md                        # Um arquivo por candidato (nomes reais so no private)
    CANDIDATE_B_ATS.pt_BR.md
    ...

scripts/
  talent.ps1                                        # WRAPPER CLI (use este!)
  ats-candidate-import.ps1                          # Pipeline completo de importacao
  extract_cv_pdf.py                                 # Extracao JSON do PDF
```

---

## Template de campos obrigatorios (ATS individual)

```markdown
# <Nome Completo> - Avaliacao ATS/LinkedIn (ATUALIZADO <DATA>)

**Nome completo:** ...
**LinkedIn:** https://www.linkedin.com/in/redacted
**Email:** ...@...
**PDF fonte:** `Linked in Profile - <Nome> 2026.pdf`
**Avaliado em:** YYYY-MM-DD

## 1. Headline LinkedIn Atual
## 2. Status Atual (empresa, localizacao, conexoes, Open to Work)
## 3. Certificacoes/Experiencias
## 4. Keywords ATS
## 5. Score ATS (tabela)
## 6. Recomendacoes Especificas (alta/media/baixa prioridade)
## 7. Alinhamento com Data Boar
## 8. Observacoes do Operador
```

---

## Apelidos do Pool (para usar no wrapper)

| Apelido | Nome (placeholder) |
|---|---|
| candidate-1 | Candidate One |
| candidate-2 | Candidate Two |
| candidate-3 | Candidate Three |
| candidate-4 | Candidate Four |
| candidate-5 | Candidate Five |
| candidate-6 | Candidate Six |
| candidate-7 | Candidate Seven |
| candidate-8 | Candidate Eight |
| candidate-9 | Candidate Nine |
| candidate-10 | Candidate Ten |
| candidate-11 | Candidate Eleven |
| candidate-12 | Candidate Twelve |
| candidate-13 | Candidate Thirteen |
| candidate-14 | Candidate Fourteen |
| candidate-15 | Candidate Fifteen |
| candidate-16 | Candidate Sixteen |
| candidate-17 | Candidate Seventeen |
| candidate-18 | Candidate Eighteen |
| candidate-19 | Candidate Nineteen |
| candidate-20 | Candidate Twenty |
| candidate-21 | Candidate Twenty-One |
| candidate-22 | Candidate Twenty-Two |
| candidate-23 | Candidate Twenty-Three |
| candidate-24 | Candidate Twenty-Four |
| candidate-25 | Candidate Twenty-Five |
| candidate-26 | Candidate Twenty-Six |

---

## Locale, jurisdição e preços (obrigatório desde 2026-04)

Ao redigir recomendações **ATS / LinkedIn** para um candidato:

1. **Mercado-alvo:** usar o par de idioma certo (ex.: **en_CA** para Canadá — não `en` genérico nem **en_UK**/**en_US** se o alvo for Canadá).
2. **Compliance:** para **Canadá**, liderar com **PIPEDA** / leis provinciais relevantes e, quando aplicável, trajetória do **Bill C-27**; **GDPR** só como complemento para papéis multinacionais/dados UE — **não** como quadro padrão do mercado canadiano.
3. **Certificações:** preços em **USD** de emissores **americanos** não são orçamento canadiano; pedir verificação no site oficial por **CAD**, centros no Canadá, impostos e descontos de capítulo. Separar cenário **USD** (ex.: prova nos EUA) do cenário **CAD**.
4. **Fonte:** em dúvida, mandar verificar página oficial do emissor ou regulador — não inventar valores.

Referência pública: **`docs/ops/LINKEDIN_ATS_PLAYBOOK.md`** secção **8** (e **`.pt_BR.md`**).

Regra: **`.cursor/rules/ats-locale-aware-recommendations.mdc`**.

## Guardrails

- **Nunca commitar** dados de candidatos (gitignored em `docs/private/`)
- **Nao criar arquivos** fora de `individual/` ou `POOL_INDEX.pt_BR.md`
- **LinkedIn:** respeitar rate limits - nao visitar todos os 24 em sequencia rapida
- **Emails:** validar antes de usar em campanhas (extraidos por regex, podem ter truncamentos)
- **Score ATS:** sempre contextualizar - score e estimado, nao definitivo
- **Open to Work:** dado senssivel - nao compartilhar sem consentimento do candidato

---

## Credenciais e Autenticacao

**LinkedIn:** Autenticacao via browser Cursor (operador faz login, sessao persiste)

**Bitwarden:** Para credenciais do UDM e outras - habilitar via:

```powershell
# Instalar Bitwarden CLI
npm install -g @bitwarden/cli
# Login
bw login
# Buscar secret
bw get password "UDM auto.cursor"
```

**Arquivo .env para credenciais locais (gitignored):**

```
docs/private/homelab/.env.api.udm-se.local  # API key UDM (ja existe)
docs/private/homelab/.env.udm.cursor        # senha auto.cursor (criar quando necessario)
```

---

*Skill versao 2.3 - 2026-04-08 | Locale/jurisdição ATS; exemplos publicos genericos; apelidos reais apenas em docs/private/*

