# ThinkPad T14 — concluir baseline LAB-OP (Ansible) e fluxo de sessão (segredos)

**English:** [T14_BASELINE_COMPLETION.md](T14_BASELINE_COMPLETION.md)

Este runbook junta **hardening repetível no host** (Ansible neste repositório) e **hábitos de operador** (credencial sudo, Bitwarden CLI, VeraCrypt opcional) **sem** colocar segredos no Git.

## 1. Concluir o baseline Ansible (no T14)

1. **Sincronizar o repo:** `git pull` no teu clone do `data-boar`.
2. **Inventário:** `ops/automation/ansible/inventory.local.ini` **precisa incluir** **`localhost ansible_connection=local`** em **`[t14]`** quando corres o playbook **no próprio portátil** (não a partir de outro PC por SSH).
3. **Preflight:** na raiz do repo, **`bash scripts/t14-ansible-preflight.sh`** — verifica Ansible, inventário, sudo, permissões de `docker.list` e presença de `bw`.
4. **Só falta o `bw` / erro em `docker.list`:** na raiz do repo, **`bash scripts/t14-bitwarden-cli-bootstrap.sh`** (instala **`@bitwarden/cli`**, corrige permissões e **`PATH`** para tmux). Depois **`source /etc/bash.bashrc`** ou novo painel tmux.
5. **Sudo:** `sudo -v` para o prompt de senha funcionar antes de uma execução longa.
6. **Aplicar:** em `ops/automation/ansible/`, **`ansible-playbook -i inventory.local.ini --ask-become-pass playbooks/t14-baseline.yml --diff`** (troubleshooting em **[ops/automation/ansible/README.md](../../ops/automation/ansible/README.md)**).

Depois de um run bem-sucedido, o **`bw`** deve estar em **`/usr/local/bin/bw`**. O role **`t14_bitwarden_cli`** atualiza **`/etc/profile.d/zz-local-bin.sh`** e **`/etc/bash.bashrc`** (para **tmux** / bash não-login). Se ainda não vês `bw`, abre um **novo painel tmux** ou corre **`source /etc/bash.bashrc`**, ou usa **`/usr/local/bin/bw`** direto.

## 2. Aquecimento de sessão: sudo + Bitwarden CLI (sem VeraCrypt)

Ordem típica:

1. **`export PATH="/usr/local/bin:$PATH"`** (ou `source` no **`profile.d`** como acima).
2. **`sudo -v`** — renova o timestamp do sudo; evita prompts a meio de instalações ou montagens.
3. **`bw login`** (uma vez por máquina) / **`bw unlock`** — depois **`export BW_SESSION=…`** conforme a documentação Bitwarden para o teu shell.

**Nota:** o **`command-not-found`** do Debian pode sugerir **`bundlewrap`** quando escreves **`bw`** — ignora; usa o caminho completo **`/usr/local/bin/bw`** se precisar.

**Flatpak + alias:** Se usares **`alias bw='flatpak run --command=bw …'`** no **`~/.bashrc`**, **`command -v bw`** pode mostrar **`alias`** — é normal (ver [OPERATOR_PACKAGE_MAINTENANCE_AND_BW_CLI.pt_BR.md](OPERATOR_PACKAGE_MAINTENANCE_AND_BW_CLI.pt_BR.md), seção **1.2.2**).

**Higiene de sessão:** Trata **`BW_SESSION`** como segredo. Ao terminar, corre **`bw lock`** (ou **`bw logout`**). Antes de capturas de tela ou de compartilhar o terminal, faz **`bw lock`** por precaução ou censura a saída; para exemplos, usa só texto fictício.

## 3. VeraCrypt + repo privado empilhado (só operador)

Caminhos, keyfiles e localização do container **não** estão aqui (ficam em notas **gitignored**). Depois do baseline e do `bw`, segue o guia VeraCrypt + Git privado em **`docs/private/homelab/`** (por exemplo **`VERACRYPT_PRIVATE_REPO_SETUP.pt_BR.md`**, seção **6.6** — fluxo T14: baseline → sudo warm → `bw` → montar).

**Scripts rastreados (sem segredos):** **`scripts/t14-install-veracrypt-console-debian13.sh`** (download/verify GPG, `apt install` do `.deb` console Debian 13 amd64) e **`scripts/t14-veracrypt-mount-private-repo.sh`** (montar **`~/.kb-cache/private_repo.vc`** com PIM + keyfile por padrão; só prompt de senha). O hash do volume (ex. SHA-512) fica definido na **criação** do volume, não na linha de montagem.

## 4. Documentos relacionados

- **[LMDE7_T14_DEVELOPER_SETUP.pt_BR.md](LMDE7_T14_DEVELOPER_SETUP.pt_BR.md)** — preparação completa T14 + LMDE (dual boot, pacotes, uv, etc.).
- **[ops/automation/ansible/README.md](../../ops/automation/ansible/README.md)** — playbook baseline, inventário, problemas de BECOME.
- **`scripts/t14-ansible-preflight.sh`** — verificações antes do playbook.
- **`scripts/t14-session-warm.sh`** — opcional: PATH (`/usr/local/bin`, exports Flatpak), `sudo -v`, verificação de `bw` (npm **ou** Flatpak), dicas tmux (sem segredos; pode ir no Git).
