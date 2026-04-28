# Protocolo de auditoria de integridade

**English:** [AUDIT_PROTOCOL.md](AUDIT_PROTOCOL.md)

Este documento rege o **alinhamento entre código e promessa técnica** do Data Boar para mantenedores, agentes e revisores. Complementa os gates já aplicados no CI (pytest, Ruff, hub de planos, guardas de PII) e **não os substitui**.

## Rigor de tradução (prosa operacional estilo LCM)

Texto em português (Brasil) voltado ao operador deve soar como **pt-BR técnico deliberado**, não como glossa palavra a palavra do inglês.

- **Evitar:** calques que leem como interface traduzida por inércia (por exemplo, *"o script permite você..."* quando a intenção é expor capacidade).
- **Preferir:** frase direta e responsável — *"o script expõe a funcionalidade..."*, *"a ferramenta assegura o rastro de auditoria..."* — mantendo **termos de produto** (Data Sniffing, Deep Boring, Safe-Hold, Audit Trail) como no glossário e nas superfícies de stakeholders.

Contrato de locale completo: **`.cursor/rules/docs-locale-pt-br-contract.mdc`**. Depois de editar **`*.pt_BR.md`** rastreados de forma relevante, rode **`uv run pytest tests/test_docs_pt_br_locale.py`**.

## Núcleo nativo (Rust)

A extensão **`boar_fast_filter`** faz parte da história de desempenho. Ao tocar no **hot path** ou no wheel empacotado:

- Rode **`cargo clippy --locked`** (e as checagens Rust documentadas no repositório) no crate nativo antes de declarar o núcleo limpo.
- Prefira **correções nativas** quando o perfil mostrar gargalo na camada Rust; mudanças em Python não devem mascarar regressão do núcleo.

## Evidência de desempenho e ADR de regressão

Qualquer mudança intencional que **enfraqueça** a interpretação publicada do A/B oficial de 200k deve vir acompanhada de:

1. **`tests/benchmarks/official_benchmark_200k.json`** regenerado (quando o perfil for re-medido), e
2. Narrativa atualizada em **`docs/ops/LAB_LESSONS_LEARNED.md`** / documentos de pós-mortem conforme necessário, e
3. Se a mudança for **trade-off** deliberado (não um bugfix), um **ADR** que registre a regressão ou a nova linha de base — ver discussão existente em **`docs/ops/SPRINT_GREAT_LEAP_POSTMORTEM.md`**.

**Leitura do 0,574:** `speedup_vs_opencore = 0,574` significa que o Pro está a **0,574× a velocidade** do OpenCore naquele artefato (Pro **mais lento**). O guard de pytest **`tests/test_official_benchmark_200k_evidence.py`** fixa a direção e campos-chave para que documentação e marketing não derivem em silêncio.

## Relacionados

- **`.cursor/rules/persona-rigor.mdc`** — persona do assistente e disciplina Safe-Hold.
- **`docs/ops/LAB_LESSONS_LEARNED.md`** — hub contínuo de evidência de lab.
- **`tests/benchmarks/run_official_bench.py`** — regenera o JSON quando houver nova medição.
