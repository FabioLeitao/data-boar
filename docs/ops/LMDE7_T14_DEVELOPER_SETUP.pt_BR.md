# ThinkPad T14 + LMDE 7 — preparação para desenvolvimento (Data Boar / lab)

**English (short pointer):** same content intent as this file; no separate EN twin unless needed for reviewers — use [TECH_GUIDE.md](../TECH_GUIDE.md) for package names in English context.

**Objetivo:** Deixar o **ThinkPad T14** com **LMDE 7** atualizado, com uma linha de base **segura** e com os **pacotes de sistema** necessários para clonar este repositório, rodar **`uv sync`**, **`pytest`**, e (opcional) **Podman/Docker** alinhados a [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md) e [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md).

**Base:** LMDE 7 (“Gigi”) usa **Debian 13 (Trixie)** — nomes de pacotes seguem `apt` como no Debian. Ajuste se a sua imagem for mais antiga ou misturar repositórios.

**Âmbito:** laptop **do operador** (não substitui [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) nem notas em `docs/private/`).

**Reinstalação “do zero” (ainda sem LMDE instalado ou sem boot no LMDE):** este arquivo **não** substitui o **instalador oficial LMDE 7** (imagem USB, boot UEFI no ThinkPad, particionamento, LUKS opcional, criação de usuário). Siga as instruções do **Linux Mint — edição LMDE** e a documentação **Lenovo** para boot por USB / Secure Boot. **Quando o T14 já estiver no LMDE 7 com sudo**, volte aqui no **§0** e siga em ordem.

## Onde está cada parte (mapa rápido):

| Seção     | Conteúdo                                                                   |
| -----     | --------                                                                   |
| **§0**    | Checklist antes de começar (disco, rede, backup).                          |
| **§1**    | `apt update` / `full-upgrade`, reboot se necessário.                       |
| **§2**    | Segurança: `ufw`, `unattended-upgrades`, `fwupd` (ThinkPad), SSH opcional. |
| **§3**    | Ferramentas de dev gerais (`git`, `build-essential`, etc.).                |
| **§4**    | Python 3.12 + libs de sistema, **`uv`**, clone, `uv sync`, `pytest`.       |
| **§5**    | Energia/conforto T14 (ex. `tlp`) — opcional.                               |
| **§6**    | Podman/Docker opcional.                                                    |
| **§7–§8** | Pacotes homelab/auditoria opcional; checklist final.                       |
| **§9**    | Links relacionados no repositório.                                         |

**Depois disto (não é instalação de SO):** stack mínima lab-op → [LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md](LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md); Grafana/Prometheus/logs → [PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md](../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md).

---

## 0. Antes de começar (checklist rápido)

| Item           | Nota                                                                                                                                        |
| ----           | ----                                                                                                                                        |
| **Instalação** | Preferir disco **criptografado** (LUKS) na instalação OEM; se já instalou sem, migrar é trabalhoso — documente a decisão em notas privadas. |
| **Rede**       | Wi‑Fi/Ethernet funcionando; **não** exponha serviços de desenvolvimento à Internet sem firewall e propósito claro.                          |
| **Backup**     | Antes de mudanças grandes no sistema, snapshot mental: **dados** em partição separada ou backup do `$HOME`.                                 |

---

## 1. Atualizar o sistema

```bash
sudo apt update
sudo apt full-upgrade -y
```

Reinicie se o kernel ou `libc` tiverem sido atualizados:

```bash
sudo reboot
```

Verifique versão:

```bash
cat /etc/os-release
uname -r
```

---

## 2. Linha de base de segurança (recomendado)

### 2.1 Firewall local (`ufw`)

Política mínima: negar entrada, permitir saída; liberar só o que precisar (ex.: **22/tcp** para SSH a partir da LAN).

```bash
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
# Se usar SSH a partir da rede de confiança:
sudo ufw allow from 192.168.0.0/16 to any port 22 proto tcp comment 'SSH LAN'
# Ajuste a sub-rede ao teu ambiente — ou restrinja ao IP do teu PC de trabalho.
sudo ufw enable
sudo ufw status verbose
```

**Data Boar em desenvolvimento:** se subires o dashboard em `0.0.0.0:8088` para testes na LAN, **não** abras **8088** na WAN; na LAN você pode liberar temporariamente:

`sudo ufw allow from 192.168.0.0/16 to any port 8088 proto tcp comment 'Data Boar lab LAN only'`

### 2.2 Atualizações de segurança automáticas (Debian)

```bash
sudo apt install -y unattended-upgrades apt-listchanges
sudo dpkg-reconfigure -plow unattended-upgrades
```

Confirme que está ativo (texto pode variar):

```bash
sudo unattended-upgrades --dry-run --debug 2>&1 | head -40
```

### 2.3 Firmware (ThinkPad + componentes)

```bash
sudo apt install -y fwupd
fwupdmgr refresh
fwupdmgr get-updates
# Se houver updates recomendados pela Lenovo/componentes:
sudo fwupdmgr update
```

Reinicie se o `fwupd` pedir. Isto ajuda **Wi‑Fi, TPM, BIOS/UEFI** quando há pacotes na LVFS.

### 2.4 SSH servidor (só se precisares)

Se **não** precisares de SSH **entrada** no T14, **não** instales `openssh-server`. Se precisares:

```bash
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

Endureça: desative login root por password, use chave, e restrinja com `ufw` (como acima).

---

## 3. Ferramentas de desenvolvimento gerais

```bash
sudo apt install -y \
  git curl ca-certificates \
  build-essential pkg-config \
  jq \
  tmux \
  htop \
  lsof \
  net-tools \
  dnsutils \
  openssh-client
```

**Editor:** instala **Cursor**, **VS Code**, **Vim**, etc. pelo método oficial — não fixamos pacote único aqui. Se usares **Cursor** em Debian/Ubuntu, vê também [CURSOR_UBUNTU_APPARMOR.pt_BR.md](CURSOR_UBUNTU_APPARMOR.pt_BR.md) (AppArmor / permissões).

---

## 4. Python 3.12 + dependências de sistema para **Data Boar**

O projeto assume **Python 3.12+** e **`uv`** ([TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md)).

### 4.1 Pacotes `apt` (alinhados ao repositório)

```bash
sudo apt install -y \
  python3.12 python3.12-venv python3.12-dev \
  libpq-dev libssl-dev libffi-dev unixodbc-dev \
  zlib1g-dev
```

- **`zlib1g-dev`:** evita erros de link `-lz` ao compilar alguns wheels (ex. caminhos `mysqlclient` / similares).
- **`unixodbc-dev`:** base para **pyodbc** / drivers ODBC (SQL Server, etc.); o **driver Microsoft** para Linux é passo à parte, conforme conector.

Se fores usar **MariaDB/MySQL** com build nativo e aparecer `mariadb_config: not found`:

```bash
sudo apt install -y libmariadb-dev
```

### 4.2 `uv` (gestor de pacotes Python)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Reabra o terminal ou:
source "$HOME/.local/bin/env" 2>/dev/null || true
uv --version
```

### 4.3 Clonar e validar o projeto

```bash
cd ~/Projects   # ou o teu diretório preferido
git clone <URL-do-teu-fork-ou-origin> data-boar
cd data-boar
uv sync
uv run pytest -q --tb=no -W error
```

Se falhar por dependência opcional, vê `pyproject.toml` — exemplos:

```bash
uv pip install -e ".[nosql]"      # MongoDB/Redis
# Rich media / OCR: seguir TECH_GUIDE se precisares
```

---

## 5. ThinkPad T14 — energia e conforto (opcional, reversível)

| Objetivo                 | Pacote / nota                                                                                                                              |
| --------                 | -------------                                                                                                                              |
| **Bateria / perfis**     | `sudo apt install -y tlp` e `sudo systemctl enable --now tlp` — ou usar apenas **Power Profiles** do Cinnamon se preferires menos camadas. |
| **Leituras de sensores** | `sudo apt install -y lm-sensors && sudo sensors-detect` (aceitar defaults com cuidado).                                                    |
| **Bluetooth / áudio**    | Geralmente já cobertos pelo LMDE; atualizações de firmware (§2.3) ajudam Wi‑Fi/BT.                                                         |

**Não** é obrigatório para desenvolvimento Data Boar; melhora experiência no hardware.

---

## 6. Contentores (lab — opcional)

Alinha com [LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md](LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md):

- **Podman** (preferido para alinhar a rootless/lab):

```bash
sudo apt install -y podman
podman --version
```

- **Docker** (se a tua equipe padronizar `docker` em vez de `podman`):

```bash
sudo apt install -y docker.io
sudo usermod -aG docker "$USER"
# Novo login para o grupo aplicar
```

Não corras **k3s** no T14 a menos que queiras consumir RAM/CPU para testes de cluster — para “só desenvolver”, **Podman** ou **Docker** basta para `build`/`run` do `Dockerfile`.

---

## 7. Pacotes úteis para auditoria / homelab (opcional)

- **Lynis** (hardening / relatório): `sudo apt install -y lynis`
- **Net-SNMP** (cliente), se fores usar [snmp-udm-lab-probe.ps1](../../scripts/snmp-udm-lab-probe.ps1) a partir de **outra** máquina ou WSL — no Linux nativo: `sudo apt install -y snmp` (MIBs opcionais: `snmp-mibs-downloader` pode exigir `non-free` no Debian 13; não é obrigatório para OIDs numéricos)

Inventário completo sugerido pelo projeto: [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md) (script `homelab-host-report.sh`).

---

## 8. Verificação final (checklist)

- [ ] `sudo apt update && apt list --upgradable` sem surpresas críticas pendentes há semanas.
- [ ] `ufw` ativo com regras mínimas; SSH (se existir) não aberto à Internet inteira.
- [ ] `fwupd` / firmware aplicados quando disponíveis.
- [ ] `python3.12 --version` ≥ 3.12; `uv --version` OK.
- [ ] No clone do repo: `uv sync` sem erro; `uv run pytest` conforme o projeto.
- [ ] `config.yaml` **não** commitado (política do `.gitignore`).

---

## 9. Documentação relacionada no repositório

| Documento                                                                                     | Uso                                                                                   |
| ---------                                                                                     | ---                                                                                   |
| [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md)                                                 | Instalação app, conectores, `uv`.                                                     |
| [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md)                        | Lista de pacotes e captura de inventário.                                             |
| [LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md](LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md)            | Podman + k3s no host de lab (opcional no T14).                                        |
| [PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md](../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md) | Grafana, Prometheus/Influx, Loki, Graylog — **depois** da baseline (§7 do doc acima). |
| [SECURITY.md](../../SECURITY.md)                                                              | API key, binding, boas práticas.                                                      |
| [PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)                                     | Onde guardar notas **não públicas**.                                                  |

---

**Última revisão:** alinhada a Debian 13 / LMDE 7 e a `pyproject.toml` do Data Boar; ajuste números de versão Python se a distro empacotar apenas `python3` com outro minor — confirme com `apt-cache policy python3.12`.
