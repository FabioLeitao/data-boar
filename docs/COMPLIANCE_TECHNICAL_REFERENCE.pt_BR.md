# Referência técnica relacionada à conformidade (TI, segurança, integração)

**English:** [COMPLIANCE_TECHNICAL_REFERENCE.md](COMPLIANCE_TECHNICAL_REFERENCE.md)

**Público:** Equipes que **integram ou operam** o Data Boar em segurança, infraestrutura ou engenharia de conformidade. Para um resumo **não técnico** voltado a **jurídico, liderança de compliance e DPOs**, veja [COMPLIANCE_AND_LEGAL.pt_BR.md](COMPLIANCE_AND_LEGAL.pt_BR.md).

Aqui ficam detalhes que não pertencem ao resumo jurídico: validação, codificações, limites de API, timeouts e onde automatizar varreduras.

---

## Controles de segurança que sustentam programas de conformidade

- **Validação de entradas** (ex.: campos tenant/technician quando aplicável).
- **Limite de tamanho do corpo** das requisições na API para reduzir risco de abuso.
- **Política de logs:** não registrar API keys, senhas nem connection strings.

Política completa e endurecimento: [SECURITY.pt_BR.md](SECURITY.pt_BR.md) ([EN](SECURITY.md)).

---

## Codificações de caractere e configs multilíngues

Arquivos de configuração e de padrões suportam **UTF-8** (recomendado), **UTF-8 com BOM** e **encodings legados** (ex.: ANSI Windows, Latin-1); o config principal usa **detecção automática** quando aplicável. Termos e idioma do relatório podem acompanhar a região (ex.: EN+FR no Canadá, PT-BR+EN no Brasil).

Passo a passo: [USAGE.pt_BR.md — Encoding de arquivos, config e padrões](USAGE.pt_BR.md#file-encoding-config-and-pattern-files) ([EN](USAGE.md)).

---

## Desempenho e resiliência

**Timeouts configuráveis** (globais e por **alvo**) para que uma fonte lenta não trave a execução inteira. Chaves e comportamento: [USAGE.pt_BR.md](USAGE.pt_BR.md) e [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md).

---

## Varreduras recorrentes / automatizadas

Execuções **agendáveis** via **API interna** permitem monitoramento contínuo ou periódico; **relatórios Excel** e **heatmaps** por sessão fazem parte do **rastro de auditoria**. API e dashboard: [USAGE.pt_BR.md](USAGE.pt_BR.md), [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md).

---

## Notificações opcionais (webhooks)

Fora de banda, ao **fim da varredura**, a aplicação pode enviar um **resumo curto** (Slack, Teams, Telegram ou webhook genérico), com suporte a **vários canais** e **cópia ao tenant** quando configurado — **desligado por padrão**; trate URLs e tokens como **segredos**. Não substitui relatórios nem política de rede/TLS. Ver [USAGE.pt_BR.md — Notificações ao operador](USAGE.pt_BR.md#notificações-ao-operador-opcional) e [SECURITY.pt_BR.md](SECURITY.pt_BR.md).

---

## Documentos relacionados

| Tema                                                | Documento                                                        |
| ----                                                | ---------                                                        |
| Resumo jurídico / compliance (tomadores de decisão) | [COMPLIANCE_AND_LEGAL.pt_BR.md](COMPLIANCE_AND_LEGAL.pt_BR.md)   |
| Frameworks, amostras, perfis YAML                   | [COMPLIANCE_FRAMEWORKS.pt_BR.md](COMPLIANCE_FRAMEWORKS.pt_BR.md) |
| Esquema completo de config, credenciais, CLI        | [USAGE.pt_BR.md](USAGE.pt_BR.md)                                 |
| Conectores, arquitetura, deploy                     | [TECH_GUIDE.pt_BR.md](TECH_GUIDE.pt_BR.md)                       |
| Padrões de detecção, ML/DL                          | [SENSITIVITY_DETECTION.pt_BR.md](SENSITIVITY_DETECTION.pt_BR.md) |

Índice completo: [README.pt_BR.md](README.pt_BR.md) · [README.md](README.md).
