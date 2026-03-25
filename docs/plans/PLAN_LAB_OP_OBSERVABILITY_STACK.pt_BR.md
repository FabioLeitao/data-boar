# Stack de observabilidade no lab-op — métricas, logs, dashboards (só plano)

**English:** [PLAN_LAB_OP_OBSERVABILITY_STACK.md](PLAN_LAB_OP_OBSERVABILITY_STACK.md)

**Objetivo:** Ordenar instrumentação **opcional** do homelab — **Grafana**, bases de séries temporais, **centralização de logs** — sem bloquear desenvolvimento do Data Boar nem a validação **–1L**. **Sem** implementação neste repositório; o operador instala via Compose, Helm no k3s ou appliance na **lab-op** (T14, Latitude, VMs Proxmox).

## Pré-requisitos (antes disto):

| Passo                                               | Documento                                                                                                                          |
| -----                                               | ---------                                                                                                                          |
| SO + baseline segura de dev no portátil             | [LMDE7_T14_DEVELOPER_SETUP.pt_BR.md](../ops/LMDE7_T14_DEVELOPER_SETUP.pt_BR.md) ([EN resumo](../ops/LMDE7_T14_DEVELOPER_SETUP.md)) |
| Stack mínima de contentores (Podman + k3s opcional) | [LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md](../ops/LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md) §1–§3                                    |
| Probes SNMP / firewall (opcional)                   | [SNMP_LAB_TARGETS.pt_BR.md](../private.example/homelab/SNMP_LAB_TARGETS.pt_BR.md)                                                  |

**Realidade de hardware:** T14 com **≤16 GB RAM** não deve correr Prometheus + Loki + Graylog + OpenSearch + Wazuh + k3s **em simultâneo**. Escolhe **um** caminho de métricas e **um** de logs; stacks pesados no **torre/VM Proxmox** quando existir.

---

## 1. Sequência recomendada (leve → pesada)

| Fase  | Stack                                                              | Função                                          | Notas                                                                                                                                                                                                                |
| ----  | -----                                                              | ------                                          | -----                                                                                                                                                                                                                |
| **A** | **Grafana** + **Prometheus** (+ `node_exporter` / `snmp_exporter`) | Métricas, dashboards, alertas (PromQL)          | **Recomendação predefinida** para homelab. Alinha com a narrativa de monitorização em [SNMP_LAB_TARGETS.pt_BR.md](../private.example/homelab/SNMP_LAB_TARGETS.pt_BR.md).                                             |
| **B** | **Grafana** + **InfluxDB** (+ **Telegraf**)                        | Métricas se preferires InfluxQL/Flux            | Alternativa válida ao TSDB do Prometheus; escolhe **um** pilar TSDB (Prometheus **ou** Influx), salvo divisão explícita (ex.: SNMP no Prometheus, métricas de app no Influx).                                        |
| **C** | **Promtail** + **Loki** + **Grafana**                              | Agregação de logs, pegada menor que ELK/Graylog | Família “LGTM”; bom para envio de **JSON/syslog** e Explore no Grafana.                                                                                                                                              |
| **D** | **Graylog** + **OpenSearch**                                       | Busca full-text, streams, pipelines             | **Graylog 5+** usa **OpenSearch** por defeito — ver documentação atual; **Elasticsearch** já não é o default universal. **Pesado:** reserva **≥8 GB** só para OpenSearch em labs pequenos; preferir **VM dedicada**. |
| **E** | **Wazuh**                                                          | Postura de segurança, vulns, hardening          | [LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md](../ops/LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md) §6 — complementa métricas/logs; não os substitui.                                                                          |

**Evitar no mesmo T14 em simultâneo:** Graylog + OpenSearch + Prometheus completo + Loki + Wazuh + k3s. Escolhe **A ou B**, **C ou D**, **E** quando houver recursos.

---

## 2. Notas de escolha de produto

- **Grafana** costuma ser o hub de **visualização**; liga a Prometheus, InfluxDB, Loki e muitos outros.
- **Elasticsearch** vs **OpenSearch:** para **Graylog**, segue o backend suportado pela versão; não assumes tutoriais “ELK” genéricos sem verificar versão.
- **InfluxDB** 3.x vs 2.x: confirma imagem/docs ao copiar Compose — há mudanças entre majors.

---

## 3. Documentação privada

URLs, retenção, LDAP e regras de firewall na LAN ficam em **`docs/private/homelab/`** (ex.: `OBSERVABILITY_RUNBOOK.md`) — **gitignored**.

---

## 4. Acompanhamento

- **PLANS_TODO.md** — linha LAB-OP observabilidade + bullet **H2**.
- **Sequenciamento (firewall → acesso → logs → Wazuh):** [PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.pt_BR.md](PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.pt_BR.md) ([EN](PLAN_LAB_FIREWALL_ACCESS_AND_OBSERVABILITY.md)) — usar quando o trabalho UniFi/L3 estiver ativo **antes** ou **em paralelo** com as fases A–E abaixo.
- **LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md** §7 — ponteiro para este plano.
- **Lembrete (quando houver hardware):** primeiro **syslog/logs** (**Promtail + Loki + Grafana**, fase **C**); depois **Wazuh** (fase **E**) numa **VM/torre** com RAM suficiente — checklist mínimo: [OBSERVABILITY_SYSLOG_DETECTION_CHECKLIST.pt_BR.md](../private.example/homelab/OBSERVABILITY_SYSLOG_DETECTION_CHECKLIST.pt_BR.md) ([EN](../private.example/homelab/OBSERVABILITY_SYSLOG_DETECTION_CHECKLIST.md)).

**Estado:** ⬜ Só plano — sem código no repo até um runbook do operador justificar um PR pequeno (ex.: Compose de exemplo **sem segredos** em `docs/private.example/`).
