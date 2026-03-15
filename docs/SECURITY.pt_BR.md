# Segurança: correções, testes e orientações para o técnico

**English:** [SECURITY.md](SECURITY.md)

Este documento resume as **medidas de segurança de severidade crítica e alta** implementadas na aplicação, os **testes de regressão** que as protegem e **recomendações para técnicos**, para que você saiba o que observar ao configurar e operar a ferramenta de auditoria.

Para política completa, versões suportadas, auditoria de dependências e como reportar vulnerabilidades, consulte **[SECURITY.md](../SECURITY.md)** ([pt-BR](../SECURITY.pt_BR.md)).

---

## O que está protegido (e como)

| Área                                          | Proteção                                                                                                                                                                                                                                   | Testes de regressão                                                                                                                                                             |
| ------                                        | ----------                                                                                                                                                                                                                                 | ----------------------                                                                                                                                                          |
| **Injeção de credenciais em URLs de conexão** | Usuário e senha de banco são **codificados para URL** ao montar as strings de conexão (conector SQL, conector MongoDB). Senhas com `@`, `:`, `/` ou `#` não quebram mais o parsing da URL nem são interpretadas como host/caminho.         | `test_sql_connector_build_url_encodes_password_special_chars`, `test_sql_connector_build_url_encodes_user_with_at`, `test_mongodb_connector_uri_encodes_password_special_chars` |
| **Injeção SQL**                               | Nomes de tabela/coluna em SQL dinâmico vêm do inspetor do banco (discover), não de entrada do usuário. Identificadores são escapados por dialeto (aspas duplas ou backtick). `session_id` é usado apenas via ORM/consultas parametrizadas. | `test_sqlite_identifier_escaping_prevents_second_statement`, `test_sql_connector_sample_uses_escaped_identifiers_sqlite`, `test_database_filters_use_orm_not_raw_sql`           |
| **Path traversal**                            | O `session_id` nos caminhos da API é validado com um padrão estrito (alfanumérico e sublinhado, 12–64 caracteres) antes do uso em caminhos de arquivo. Valores inválidos retornam HTTP 400.                                                | `test_session_id_validation_rejects_dangerous_patterns`                                                                                                                         |
| **Config / YAML**                             | O config é carregado apenas com `yaml.safe_load` (sem deserialização de objetos Python arbitrários). Tags YAML maliciosas (ex.: execução de código) são rejeitadas.                                                                        | `test_config_save_uses_safe_load`, `test_config_loader_uses_safe_load_not_load`                                                                                                 |
| **Exposição do endpoint de config**           | Quando `api.require_api_key` é true, GET `/config` retorna **401** sem uma chave de API válida, de modo que o arquivo de config bruto (que pode conter senhas e segredos) não fica exposto a usuários não autenticados.                    | `test_config_endpoint_requires_api_key_when_required`                                                                                                                           |

Todos esses testes estão em **`tests/test_security.py`**. Executar `pytest tests/test_security.py -v` com frequência (ex.: no CI) ajuda a garantir que essas proteções não sejam removidas por engano.

---

## Recomendações para técnicos

- **Senhas com caracteres especiais:** Você pode usar com segurança senhas de banco ou MongoDB que contenham `@`, `:`, `/` ou `#`. A aplicação as codifica ao montar as URLs de conexão. Nenhuma configuração extra é necessária.
- **Proteger o config na interface:** A página **Configuração** (GET `/config`) exibe e permite editar o arquivo de config principal, que pode conter credenciais. Se a API estiver exposta a usuários ou redes não confiáveis, defina **`api.require_api_key: true`** e forneça uma chave de API forte (ou `api.api_key_from_env`). Assim, apenas requisições que enviarem **X-API-Key** ou **Authorization: Bearer** válidos poderão acessar `/config`.
- **Onde o config fica armazenado:** O caminho do arquivo de config é definido na inicialização (padrão `config.yaml` ou `CONFIG_PATH`). Garanta que as permissões do arquivo e do diretório restrinjam leitura/escrita apenas a usuários confiáveis.
- **Session IDs nas URLs:** A API usa `session_id` em caminhos (ex.: `/reports/{session_id}`). Apenas valores que seguem o padrão permitido (alfanumérico e sublinhado, 12–64 caracteres) são aceitos; qualquer outro retorna 400. Isso evita path traversal por session IDs forjados.
- **Implantação:** Quando o dashboard ou a API estiver exposto à internet ou a redes não confiáveis, execute atrás de um **proxy reverso** com **TLS** e autenticação adequada. Use a chave de API opcional e o rate limiting como camada extra; veja **SECURITY.md** e **docs/deploy/DEPLOY.md** (Security and hardening).

---

## Documentação relacionada

- **Índice da documentação** (todos os tópicos, ambos os idiomas): [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md).
- **SECURITY.md** ([pt-BR](../SECURITY.pt_BR.md)) — Política de segurança, cabeçalhos, chave de API opcional, reporte de vulnerabilidades.
- **docs/deploy/DEPLOY.md** ([pt-BR](deploy/DEPLOY.pt_BR.md)) — Implantação e endurecimento (Docker, Kubernetes, proxy reverso).
- **docs/USAGE.md** ([pt-BR](USAGE.pt_BR.md)) — CLI, API e configuração (incluindo `api.require_api_key`).
- **Páginas de manual:** `man data_boar` ou `man lgpd_crawler` (seção 1), `man 5 data_boar` ou `man 5 lgpd_crawler` (seção 5) — incluem notas breves sobre segurança e credenciais.
