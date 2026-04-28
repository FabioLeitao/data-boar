# Protocolo de Auditoria de Integridade

Este documento rege a conformidade entre o código e a promessa técnica do Data Boar.

## Rigor de Tradução (LCM)

As traduções para PT-BR devem seguir o **Linguistic Category Model** de alto impacto:

- **Evitar:** "O script permite você..." (Tradução direta).
- **Adotar:** "O script expõe a funcionalidade...", "A ferramenta assegura o rastro...".

## Gestão de Performance

Qualquer queda na eficiência do `boar_fast_filter` deve disparar um **ADR de Regressão**.

## Contrato de Bancada (Adam Savage)

- Ferramenta que não funciona não permanece na bancada.
- Scripts órfãos ou quebrados devem ser removidos ou corrigidos antes de encerrar a tarefa.

## Registro de Ritual e Contrato

Toda alteração de ritual operacional ou contrato de execução deve ser registrada neste arquivo
antes do fechamento da sessão.

## Warning de Integridade (Doutrina NASA)

Quando o Founder solicitar uma ação que viole a doutrina de integridade (por exemplo, pular
testes obrigatórios), o agente deve emitir um **Warning de Integridade** antes de executar.
