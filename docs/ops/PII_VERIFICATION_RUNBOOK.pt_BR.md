# Runbook de Verificacao de PII

Runbook operacional para verificar PII/dados sensiveis em repositório publico com cadencia curta, media e longa.

## Gate de revisao manual (obrigatorio)

Antes de marcar qualquer execucao como SAFE, revise os criterios locais/privados que nao ficam em docs versionados.

- [ ] Revisei os criterios locais atuais em `docs/private/security_audit/`.
- [ ] Atualizei seeds locais de allow/deny (se necessario) em notas/arquivos privados.
- [ ] Confirmei que nenhum novo identificador sensivel precisa entrar nos guardrails versionados.

Se algum item estiver desmarcado, **nao** marque SAFE.

## Escopo e objetivo

- Este runbook cobre arquivos tracked e historico Git em **clone fresco**.
- Ele complementa os guardrails (`new-b2-verify`, `pii_history_guard.py`, `test_pii_guard.py`).
- Ele nao substitui classificacao manual para termos contextuais.
- `new-b2-verify.ps1` e somente PowerShell (ideal no L14/Windows). Em Linux, use o equivalente manual abaixo.

## 0) Pre-condicoes

Executar em clone fresco:

```powershell
cd C:\temp
if (Test-Path .\teste_operator_fresh) { Remove-Item -Recurse -Force .\teste_operator_fresh }
mkdir teste_operator_fresh | Out-Null
cd .\teste_operator_fresh
git clone git@github.com:FabioLeitao/data-boar.git
cd .\data-boar
git status
```

Esperado: working tree limpo em `main`.

### Linux (hosts lab-op)

```bash
cd /tmp
rm -rf teste_operator_fresh
mkdir -p teste_operator_fresh
cd teste_operator_fresh
git clone git@github.com:FabioLeitao/data-boar.git
cd data-boar
git status
```

Esperado: working tree limpo em `main`.

## 1) Short run (semanal / antes de PR sensivel)

```powershell
.\scripts\new-b2-verify.ps1 -TargetUserSegment fabio
uv run python .\scripts\pii_history_guard.py
uv run pytest tests/test_pii_guard.py -q
# Rode o grep de padrao UC a partir do seu bundle local/privado de criterios.
git grep -n -E "\b(192\.168\.[0-9]{1,3}\.[0-9]{1,3}|10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3})\b" -- scripts docs tests .cursor
git grep -n -E "\b[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}\b" -- scripts docs tests .cursor
```

Condicao de PASS: sem match relevante + testes OK.

### Linux (equivalente ao `new-b2-verify.ps1`)

```bash
TARGET_SEGMENT="fabio"
TARGET_PATH_UPPER="C:\\Users\\${TARGET_SEGMENT}"
TARGET_PATH_LOWER="c:\\users\\${TARGET_SEGMENT}"

git log --all -S "${TARGET_PATH_UPPER}" --oneline
git log --all -S "${TARGET_PATH_LOWER}" --oneline
git grep -n -i -F "${TARGET_PATH_UPPER}" $(git rev-list --all)

uv run python ./scripts/pii_history_guard.py
uv run pytest tests/test_pii_guard.py -q
# Rode o grep de padrao UC a partir do seu bundle local/privado de criterios.
git grep -n -E "\b(192\.168\.[0-9]{1,3}\.[0-9]{1,3}|10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3})\b" -- scripts docs tests .cursor
git grep -n -E "\b[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}\b" -- scripts docs tests .cursor
```

## 2) Mid run (mensal)

```powershell
git grep -n -E "linkedin\.com/in/" -- . ":(exclude)docs/private/**"
git grep -n -i -E "c:\\users\\[^\\]+|/home/[^/]+" -- . ":(exclude)docs/private/**"
```

Depois, classificar cada hit como:

- placeholder/teste/exemplo aceitavel; ou
- exposicao real sensivel que exige correcao imediata.

## 3) Long run (trimestral ou pos-incidente)

Rodar checagens de historico completo para seeds de alto risco relevantes para sua politica privada:

```powershell
git log --all -S "C:\Users\fabio" --oneline
git log --all -S "c:\users\fabio" --oneline
git log --all -S "/home/leitao" --oneline
git log --all -S "linkedin.com/in/" --oneline
# Rode a verificacao de seed UC a partir do seu bundle local/privado de criterios.
```

Mantenha qualquer seed especifica de pessoa/caso apenas em notas/arquivos privados.

## Termos sensiveis ao contexto (classificacao manual)

Alguns termos podem ser permitidos somente em contexto restrito (por exemplo, contexto de carreira/portfolio), e nao em contexto juridico/medico/privado.

Quando esses termos aparecerem:

1. classifique por contexto;
2. registre a decisao em notas privadas;
3. corrija arquivos tracked se o contexto nao for permitido.

## Decisao final de SAFE

Marque SAFE somente se:

- o gate de revisao manual estiver totalmente marcado;
- o short run passar;
- as checagens mid/long nao mostrarem exposicao real;
- os termos contextuais tiverem classificacao manual concluida.

Se algum criterio falhar, o status e NOT SAFE e exige remediacao cirurgica + novo ciclo de validacao.
