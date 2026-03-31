# ThinkPad T14 + LMDE 7 — preparação para desenvolvimento (Data Boar / lab)

**English (short pointer):** same content intent as this file; no separate EN twin unless needed for reviewers — use [TECH_GUIDE.md](../TECH_GUIDE.md) for package names in English context.

**Objetivo:** Deixar o **ThinkPad T14** com **LMDE 7** atualizado, com uma linha de base **segura** e com os **pacotes de sistema** necessários para clonar este repositório, rodar **`uv sync`**, **`pytest`**, e (opcional) **Podman/Docker** alinhados a [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md) e [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md).

**Base:** LMDE 7 (“Gigi”) usa **Debian 13 (Trixie)** — nomes de pacotes seguem `apt` como no Debian. Ajuste se a sua imagem for mais antiga ou misturar repositórios.

**Âmbito:** laptop **do operador** (não substitui [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) nem notas em `docs/private/`).

**Reinstalação “do zero”:** segue o **§0** (Ventoy + UEFI + **Secure Boot** ligado) e o instalador gráfico do **LMDE 7**. **Quando o T14 já estiver no LMDE 7 com sudo**, continua no **§1**.

## Onde está cada parte (mapa rápido):

| Seção      | Conteúdo                                                                                  |
| -----      | --------                                                                                  |
| **§0**     | Instalação: **Ventoy** (USB), **UEFI**, **Secure Boot** ativo, LMDE 7 no ThinkPad **T14**. |
| **§1**     | Checklist antes de começar (disco, rede, backup).                                         |
| **§2**     | `apt update` / `full-upgrade`, reboot se necessário.                                      |
| **§3**     | Segurança: `ufw`, `unattended-upgrades`, `fwupd`, Lynis, sysctl conservador; SSH opcional. |
| **§4**     | Ferramentas de dev gerais (`git`, `build-essential`, etc.).                               |
| **§5**     | Python **3.13** (recomendado; **≥3.12** ok) + libs de sistema, **`uv`**, clone, `uv sync`, `pytest`. |
| **§6**     | T14: energia (**`tlp`**), **I/O NVMe**, **kernel/sysctl** (performance prudente).       |
| **§7**     | Podman/Docker opcional.                                                                   |
| **§8–§9**  | Pacotes homelab/auditoria; checklist final.                                               |
| **§10**    | Links relacionados no repositório.                                                        |

**Depois disto (não é instalação de SO):** stack mínima lab-op → [LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md](LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md); Grafana/Prometheus/logs → [PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md](../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md).

---

## 0.x Decisão de instalação: dual boot (Windows 11 + LMDE) vs LMDE-only

**Recomendação padrão para este projeto:** manter **dual boot** (Windows 11 + LMDE) quando o T14 for uma **workstation do operador**.

- **Por quê**: reduz risco operacional (firmware/BIOS tools, recovery, apps específicas de Windows), sem impedir que o LMDE seja o ambiente principal para dev/lab.
- **Como mitigar drift**: trate o Windows como **fallback** (mínimo necessário), e concentre o fluxo Data Boar no LMDE.

**Quando faz sentido LMDE-only:** quando o T14 for um host dedicado de laboratório (quase “appliance”) e você quiser minimizar variação operacional. Nesse caso, registre a decisão em nota privada (custo/benefício + riscos) e mantenha backups.

## 0. Instalação no T14 — Ventoy, UEFI e **Secure Boot** ligado

**Objetivo:** preparar o USB com **Ventoy**, manter **Secure Boot ativo** no ThinkPad durante a instalação **e** depois no Linux, sem pedir que desligues o Secure Boot de forma permanente. **“Device Guard”** (e **Credential Guard**) são nomes de recursos **do Windows**; no **LMDE** não existem com esses nomes — o paralelo é **Secure Boot + TPM (se usares LUKS/TPM) + endurecimento em camadas (§3)**. Na **máquina onde geras o USB** (ex. Windows 11 com **HVCI/Device Guard**), **você pode manter** essas políticas; o **Ventoy2Disk** não exige desligá-las.

### 0.1 Versão do Ventoy (confirma no dia)

A linha de releases mudou de **`1.0.x`** para **`1.1.x`**. Em **dezembro de 2025** a release estável citada na comunidade era **v1.1.10** — **no dia da instalação** confirma em **[Ventoy — GitHub Releases](https://github.com/ventoy/Ventoy/releases)** ou **[ventoy.net — download](https://www.ventoy.net/en/download.html)**. Se o teu stick já tiver uma 1.1.x recente, **você pode atualizar o Ventoy no USB** (mesma ferramenta `Ventoy2Disk`) antes de copiar a ISO do LMDE.

### 0.2 Preparar o USB com **suporte a Secure Boot**

O suporte documental oficial: **[Ventoy — about Secure Boot (UEFI)](https://www.ventoy.net/en/doc_secure.html)** (desde **1.0.07**; opção **ligada por defeito** desde **1.0.76** no `Ventoy2Disk`).

**Windows (GUI):**

1. Extrai o ZIP do Ventoy correspondente à tua arquitetura (normalmente **x86_64**).
1. Executa **`Ventoy2Disk.exe`** como administrador.
1. Escolhe o disco USB correto (cuidado a não apontar para outro disco).
1. Em **Option → Secure Boot Support**: mantém **ativo** (as versões recentes já vêm assim).
1. **Install** (ou **Update** se já for um stick Ventoy).

**Linux (script):**

```bash
# Dentro da pasta descompactada do Ventoy:
sudo bash Ventoy2Disk.sh -i -s /dev/sdX   # substitui sdX pelo dispositivo USB certo; -s = Secure Boot
```

1. Copia a imagem **`lmde-7-*.iso`** (oficial **Linux Mint LMDE**) para a partição de dados do Ventoy (exFAT/NTFS — a que aparece no Windows/macOS/Linux).

### 0.3 Firmware do T14 antes do boot

1. Opcional mas recomendado: na **Windows** ou com **fwupd** noutro Linux, verifica se há **BIOS/UEFI** novo para **T14** (melhorias TPM, UEFI e arranque).
1. Reinicia, **F1**/**Enter** (varia por geração) para **UEFI/BIOS Setup**.
1. **Boot mode:** **UEFI only** — **não** uses Legacy/CSM para esta instalação.
1. **Secure Boot:** **Enabled** (mantém **ligado**).
1. Grava e sai.

### 0.4 Primeiro arranque do Ventoy com Secure Boot

1. Liga o USB, **boot** pelo dispositivo UEFI (menu de boot do ThinkPad).
1. **Na primeira vez** por máquina, o Ventoy pode mostrar o fluxo **“Enroll Key”** ou **“Enroll Hash”** (tela azul, conforme doc oficial). Segue **uma** das vias até ao fim — em muitos ThinkPads **Enroll Hash** é o que menos atrito dá.
1. Se aparecer erro estilo **“Linpus lite”** ou recusa contínua: atualiza **Ventoy** no USB, confirma **UEFI only**, e revê a doc **Secure Boot** do Ventoy; **não** assumas que precisas desligar Secure Boot de forma permanente — primeiro tenta **regravar** o USB com release mais nova.

### 0.5 Instalar o LMDE 7 a partir do menu Ventoy

1. No menu Ventoy, escolhe a ISO **LMDE 7**.
1. No instalador: idioma, teclado, rede.
1. **Disco:** recomenda-se **criptografia LUKS** (passphrase forte; regista num **local seguro** — ex. gestor de segredos). Isto alinha com **TPM** presente no T14 para arranque **posterior** conforme opções que o instalador oferecer.
1. Cria o usuário; ao fim, reinicia e **remove o USB** quando pedido.

### 0.6 Depois da instalação — Secure Boot com Debian/LMDE

O LMDE baseado em **Debian** usa normalmente **`shim`** + kernel assinado: com **Secure Boot ligado**, o sistema instalado deve **continuar a arrancar** sem desligar Secure Boot no firmware. Se **após** a instalação o firmware reclamar:

1. Confirma que não há **outro** bootloader não assinado a “saltar” à frente do `shim`.
1. Corre **`sudo dpkg-reconfigure shim-unsigned`** / pacotes **`shim-signed`** conforme a tua imagem (nomes exactos: `apt search shim` no LMDE).
1. Mantém **Secure Boot: Enabled** no UEFI; só em último caso segue notas do Debian para **MOK** (procedimento consciente, não “desligar tudo”).

### 0.7 Resumo de requisitos que pediste

| Requisito | Onde fica coberto |
| --------- | ----------------- |
| USB com **Ventoy** atualizado | §0.1–0.2; confirmar versão no site oficial no dia |
| **Secure Boot** ligado na instalação | §0.2–0.5 |
| **Secure Boot** ligado na operação diária | §0.6 + §3 |
| **Device Guard** (Windows) ligado *enquanto preparas* o USB | Nota no início do §0 — no LMDE não há homónimo directo |

---

## 1. Antes de começar (checklist rápido)

| Item           | Nota                                                                                                                                        |
| ----           | ----                                                                                                                                        |
| **Instalação** | Preferir disco **criptografado** (LUKS) na instalação OEM; se já instalou sem, migrar é trabalhoso — documente a decisão em notas privadas. |
| **Rede**       | Wi‑Fi/Ethernet funcionando; **não** exponha serviços de desenvolvimento à Internet sem firewall e propósito claro.                          |
| **Backup**     | Antes de mudanças grandes no sistema, snapshot mental: **dados** em partição separada ou backup do `$HOME`.                                 |

---

## 2. Atualizar o sistema

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

## 3. Linha de base de segurança (recomendado)

### 3.1 Firewall local (`ufw`)

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

### 3.2 Atualizações de segurança automáticas (Debian)

```bash
sudo apt install -y unattended-upgrades apt-listchanges
sudo dpkg-reconfigure -plow unattended-upgrades
```

Confirme que está ativo (texto pode variar):

```bash
sudo unattended-upgrades --dry-run --debug 2>&1 | head -40
```

### 3.3 Firmware (ThinkPad + componentes)

```bash
sudo apt install -y fwupd
fwupdmgr refresh
fwupdmgr get-updates
# Se houver updates recomendados pela Lenovo/componentes:
sudo fwupdmgr update
```

Reinicie se o `fwupd` pedir. Isto ajuda **Wi‑Fi, TPM, BIOS/UEFI** quando há pacotes na LVFS.

### 3.4 SSH servidor (só se precisares)

Se **não** precisares de SSH **entrada** no T14, **não** instales `openssh-server`. Se precisares:

```bash
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

Endureça: desative login root por password, use chave, e restrinja com `ufw` (como acima).

### 3.5 Lynis (relatório de hardening)

Útil antes de o T14 entrar no **lab-op** — não substitui política nem pen-test, mas dá uma lista priorizável.

```bash
sudo apt install -y lynis
sudo lynis audit system
# Relatório em /var/log/lynis.log — rever sugestões e aplicar só o que fizer sentido para *estação de dev*
```

Tende a “reclamar” de coisas aceitáveis em laptop de desenvolvimento; usa o relatório como **checklist**, não como obrigação cega.

### 3.6 `sysctl` — rede e VM (valores **conservadores**)

Mede impacto antes de afinar agressivamente. Exemplo **seguro para desktop** com RAM razoável (ajusta ou omite linhas após testar):

```bash
sudo tee /etc/sysctl.d/99-workstation-t14.conf >/dev/null <<'EOF'
# VM — desktop com 16–32 GiB RAM típico
vm.swappiness=20
vm.vfs_cache_pressure=50
# Rede local / lab (não abre serviços — só comportamento de pilha)
net.ipv4.tcp_fastopen=1
net.core.somaxconn=4096
EOF
sudo sysctl --system
```

Se notares troca excessiva, volta `vm.swappiness` para o padrão (~60) ou remove o arquivo.

### 3.7 Pacote `auditd`, `debsecan`, `needrestart` (opcional)

```bash
sudo apt install -y debsecan needrestart
sudo debsecan --suite trixie 2>/dev/null | head -40   # ajusta o suite ao que /etc/os-release reportar
```

Depois de **upgrades** de kernel/libs, o **`needrestart`** indica o que precisa de reinício de serviço — útil para não ficares com `sshd` ou libs antigas carregadas.

**AppArmor:** o perfil por defeito do Debian/LMDE costuma estar ativo; não desligues sem motivo. Para Cursor/AppArmor vê também [CURSOR_UBUNTU_APPARMOR.pt_BR.md](CURSOR_UBUNTU_APPARMOR.pt_BR.md).

---

## 4. Ferramentas de desenvolvimento gerais

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

## 5. Python 3.13 (recomendado) + dependências de sistema para **Data Boar**

O projeto suporta **Python ≥3.12**; **3.13** é o alvo recomendado no laptop para **paridade com a imagem Docker** publicada. Usa **`uv`** ([TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md)).

### 5.1 Pacotes `apt` (alinhados ao repositório)

Confirma que **3.13** está nos repositórios: `apt-cache policy python3.13`. Se não existir (distro antiga), instala **`python3.12`** / **`python3.12-venv`** / **`python3.12-dev`** no lugar da linha abaixo.

```bash
sudo apt install -y \
  python3.13 python3.13-venv python3.13-dev \
  libpq-dev libssl-dev libffi-dev unixodbc-dev \
  zlib1g-dev
```

- **`zlib1g-dev`:** evita erros de link `-lz` ao compilar alguns wheels (ex. caminhos `mysqlclient` / similares).
- **`unixodbc-dev`:** base para **pyodbc** / drivers ODBC (SQL Server, etc.); o **driver Microsoft** para Linux é passo à parte, conforme conector.

Se fores usar **MariaDB/MySQL** com build nativo e aparecer `mariadb_config: not found`:

```bash
sudo apt install -y libmariadb-dev
```

### 5.2 `uv` (gestor de pacotes Python)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Reabra o terminal ou:
source "$HOME/.local/bin/env" 2>/dev/null || true
uv --version
```

### 5.3 Clonar e validar o projeto

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

## 6. ThinkPad T14 — energia, I/O e kernel (opcional, reversível)

| Objetivo                 | Pacote / nota                                                                                                                              |
| --------                 | -------------                                                                                                                              |
| **Bateria / perfis**     | `sudo apt install -y tlp` e `sudo systemctl enable --now tlp` — ou usar apenas **Power Profiles** do Cinnamon se preferires menos camadas. |
| **Leituras de sensores** | `sudo apt install -y lm-sensors && sudo sensors-detect` (aceitar defaults com cuidado).                                                    |
| **Bluetooth / áudio**    | Geralmente já cobertos pelo LMDE; atualizações de firmware (§3.3) ajudam Wi‑Fi/BT.                                                         |

**Não** é obrigatório para desenvolvimento Data Boar; melhora experiência no hardware.

### 6.2 I/O em NVMe (scheduler e `fstab`)

NVMe moderno em kernel recente usa frequentemente **`none`** (multiqueue). Verifica:

```bash
for d in /sys/block/nvme*n*/queue/scheduler; do echo "$d: $(cat "$d")"; done
```

Se puderes escolher, **`none`** ou **`mq-deadline`** são típicos em NVMe; **não** forces `bfq` em NVMe sem medição.

Em **`/etc/fstab`**, para sistemas de arquivos em SSD, muitos operadores usam **`noatime`** (ou **`relatime`**, já default em muitos casos) para menos escritas metadata:

```text
# exemplo de opções numa linha de partição raiz — confirma UUID com `blkid`
UUID=XXXX  /  ext4  defaults,noatime  0 1
```

Revalida com `findmnt` e um reboot após editar o `fstab`.

### 6.3 Kernel — linha Debian + módulos (T14)

Mantém o kernel **dos repositórios LMDE/Debian** para assinaturas alinhadas ao **Secure Boot**. Evita liquorix/random mainline **a menos que** saibas re-assinar ou aceitas gerir MOK.

Lista módulos pensados para ThinkPad (carregados ou built-in):

```bash
lsmod | egrep 'thinkpad_acpi|think_lmi|nvme|iwlwifi' || true
```

Se **Wi‑Fi** falhar após reboot novo, volta a §6.2/§3.3 (firmware `linux-firmware` / `fwupd`).

### 6.4 `zram` (swap comprimida — opcional)

Útil em máquinas com RAM mais justa; em 32 GiB pode ser desnecessário.

```bash
sudo apt install -y zram-tools
```

Lê **`/usr/share/doc/zram-tools/README.*`** (o nome do serviço varia entre releases Debian/LMDE — pode ser *generator* *systemd* ou script legacy). Objetivo: menos **I/O de swap em disco** em picos de compilação; se o pacote confundir ou não precisares, remove e mantém só o afinamento de **`vm.swappiness`** (§3.6).

### 6.5 Pronto para **lab-op** (SSH + inventário)

Quando o T14 for host de laboratório:

1. Confirma **`openssh-server`** só se a política do lab o exigir; **`PermitRootLogin no`**, **`PasswordAuthentication no`**, chaves só.
1. Copia do repositório o manifest de exemplo **`docs/private.example/homelab/lab-op-hosts.manifest.example.json`** para **`docs/private/homelab/lab-op-hosts.manifest.json`** (gitignored) e acrescenta o T14.
1. A partir do teu PC de trabalho: **`scripts/lab-op-sync-and-collect.ps1`** ou **`homelab-host-report.sh`** conforme [HOMELAB_VALIDATION.pt_BR.md](HOMELAB_VALIDATION.pt_BR.md).

---

## 7. Contentores (lab — opcional)

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

## 7.1 Automação repetível (Ansible + OpenTofu) — opcional, recomendado para “não esquecer passos”

Se você quer **repetibilidade** (reinstalar o T14, padronizar baseline, ou reaplicar ajustes sem “lembrar de cabeça”), uma dupla comum é:

- **Ansible**: configurações no host (pacotes, arquivos, serviços, hardening leve).
- **OpenTofu**: infraestrutura declarativa (quando você tem APIs/provedores; útil para lab com providers suportados).

**Guardrails (sem regressão e sem segredos):**

- **Não** coloque segredos (tokens, chaves, senhas) em arquivos rastreados neste repo. Prefira:
  - variáveis de ambiente no terminal da sessão,
  - vault externo,
  - ou árvore **gitignored** (`docs/private/…`) se for só para você.
- Trate a automação como **insumo**: execute, valide, e só então torne “padrão”.

### 7.1.1 Ansible (host bootstrap)

Instalação (preferir `apt`):

```bash
sudo apt update
sudo apt install -y ansible
ansible --version
```

**Esqueleto mínimo** (recomendação: manter em um repositório separado `lab-automation/` ou em `docs/private/`):

```text
lab-automation/
  ansible/
    inventory.ini
    bootstrap-t14.yml
    group_vars/
      all.yml
```

`inventory.ini` (localhost):

```ini
[t14]
localhost ansible_connection=local
```

`bootstrap-t14.yml` (exemplo intencionalmente curto):

```yaml
---
- name: Bootstrap T14 (LMDE 7)
  hosts: t14
  become: true
  tasks:
    - name: Install baseline packages
      ansible.builtin.apt:
        update_cache: true
        name:
          - git
          - curl
          - ca-certificates
          - build-essential
          - jq
          - ufw
          - unattended-upgrades
          - fwupd
        state: present

    - name: Enable UFW with safe defaults
      ansible.builtin.shell: |
        set -euo pipefail
        ufw default deny incoming
        ufw default allow outgoing
        ufw --force enable
      args:
        executable: /bin/bash
```

Execução:

```bash
cd lab-automation/ansible
ansible-playbook -i inventory.ini bootstrap-t14.yml
```

### 7.1.2 OpenTofu (infra declarativa)

**Nota honesta:** OpenTofu vale quando você tem um provider real para o alvo (ex.: DNS/Cloud, GitHub, algum appliance com API). Para “só configurar o Linux”, Ansible costuma bastar.

Instalação:

- Primeiro tente `apt` (se existir na tua base Debian/LMDE):

```bash
sudo apt update
sudo apt install -y opentofu || true
tofu version
```

- Se não existir no `apt`, siga o método oficial de instalação do OpenTofu (binário assinado / checksum) e **documente** o caminho que você adotou em `docs/private/` para repetibilidade.

**Esqueleto mínimo**:

```text
lab-automation/
  tofu/
    versions.tf
    main.tf
    outputs.tf
```

`versions.tf` (exemplo genérico):

```hcl
terraform {
  required_version = ">= 1.6.0"
}
```

Execução (com variáveis fora do Git quando houver segredos):

```bash
cd lab-automation/tofu
tofu init
tofu plan
tofu apply
```

### 7.1.3 “Não esquecer” (checklist de validação pós-automação)

Depois de rodar automações, valide manualmente (mesma lógica do §9):

- `mokutil --sb-state` (Secure Boot ainda **enabled**)
- `ufw status verbose`
- `unattended-upgrades --dry-run --debug` (sem erro óbvio)
- `fwupdmgr get-updates` (sem falha)
- `uv sync` + `uv run pytest` no repo Data Boar

Se qualquer item “quebrar”, ajuste o playbook/tofu e reexecute — objetivo é **idempotência**.

## 8. Pacotes úteis para auditoria / homelab (opcional)

- **Lynis** — vê **§3.5** (instalação e auditoria)
- **Net-SNMP** (cliente), se fores usar [snmp-udm-lab-probe.ps1](../../scripts/snmp-udm-lab-probe.ps1) a partir de **outra** máquina ou WSL — no Linux nativo: `sudo apt install -y snmp` (MIBs opcionais: `snmp-mibs-downloader` pode exigir `non-free` no Debian 13; não é obrigatório para OIDs numéricos)

Inventário completo sugerido pelo projeto: [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md) (script `homelab-host-report.sh`).

---

## 9. Verificação final (checklist)

- [ ] **UEFI / Secure Boot:** `mokutil --sb-state` mostra **enabled**; se usaste **Ventoy + enrolment**, confirmas que o assistente ficou concluído e não desligaste Secure Boot para “facilitar”.
- [ ] **Ventoy:** versão no stick alinhada ao release atual em [Ventoy releases](https://github.com/ventoy/Ventoy/releases) (atualiza com **`Ventoy2Disk`** no teu Windows de manutenção quando fizer sentido).
- [ ] `sudo apt update && apt list --upgradable` sem surpresas críticas pendentes há semanas.
- [ ] `ufw` ativo com regras mínimas; SSH (se existir) não aberto à Internet inteira.
- [ ] `fwupd` / firmware aplicados quando disponíveis.
- [ ] (Opcional) **`lynis audit system`** sem regressão óbvia após mudanças grandes (§3.5).
- [ ] Python: **`python3.13 --version` ≥ 3.13** (recomendado) ou **`python3.12 --version` ≥ 3.12**; `uv --version` OK.
- [ ] No clone do repo: `uv sync` sem erro; `uv run pytest` conforme o projeto.
- [ ] `config.yaml` **não** commitado (política do `.gitignore`).
- [ ] **Lab-op:** manifesto (`lab-op-hosts.manifest.json`) e SSH/chaves prontos se o T14 for host de coleta (§6.5).

---

## 10. Documentação relacionada no repositório

| Documento                                                                                     | Uso                                                                                   |
| ---------                                                                                     | ---                                                                                   |
| [TECH_GUIDE.pt_BR.md](../TECH_GUIDE.pt_BR.md)                                                 | Instalação app, conectores, `uv`.                                                     |
| [HOMELAB_HOST_PACKAGE_INVENTORY.md](HOMELAB_HOST_PACKAGE_INVENTORY.md)                        | Lista de pacotes e captura de inventário.                                             |
| [LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md](LAB_OP_MINIMAL_CONTAINER_STACK.pt_BR.md)            | Podman + k3s no host de lab (opcional no T14).                                        |
| [PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md](../plans/PLAN_LAB_OP_OBSERVABILITY_STACK.pt_BR.md) | Grafana, Prometheus/Influx, Loki, Graylog — **depois** da baseline (§7 do doc acima). |
| [OPERATOR_PACKAGE_MAINTENANCE_AND_BW_CLI.pt_BR.md](OPERATOR_PACKAGE_MAINTENANCE_AND_BW_CLI.pt_BR.md) | Atualizações no workstation, **Topgrade**, **`gta`**, **Bitwarden CLI** (`bw`).       |
| [SECURITY.md](../../SECURITY.md)                                                              | API key, binding, boas práticas.                                                      |
| [PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)                                     | Onde guardar notas **não públicas**.                                                  |

---

**Última revisão:** alinhada a Debian 13 / LMDE 7 e a `pyproject.toml` do Data Boar (**≥3.12**, **3.13** recomendado em host); confirme pacotes com `apt-cache policy python3.13` (ou `python3.12` em fallback).
