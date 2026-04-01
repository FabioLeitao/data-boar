# Rascunho: instalador do LMDE não mostra dm-crypt (`/dev/mapper/*`) no particionamento manual

Este é um **rascunho** para colar num bug tracker do instalador do LMDE/Linux Mint (Ubiquity / UI de particionamento). Ele evita de propósito segredos e detalhes sensíveis do ambiente.

## Onde reportar

- Primário: abrir issue no `linuxmint/ubiquity` (GitHub).
- Guia: `https://linuxmint.github.io/reporting-an-issue.html` (regras gerais de “como reportar” e como escolher o projeto certo).

## Resumo

Ao instalar **LMDE** com **particionamento manual**, dispositivos **dm-crypt** já desbloqueados (por exemplo `cryptsetup open … cryptroot` → `/dev/mapper/cryptroot`) **não aparecem** na lista de partições do instalador, então não dá para selecioná-los como `/`.

Isso empurra o usuário a selecionar o device “cru” por baixo (ex.: `/dev/nvme0n1p6`) e formatar — o que destrói o header do LUKS e inviabiliza o fluxo de criptografia de disco desejado.

## Ambiente

- **Distro / instalador**: LMDE 7 “Gigi” live ISO (instalador “Install Linux Mint” / UI de particionamento manual)
- **Firmware**: UEFI, Secure Boot habilitado
- **Layout do disco** (um NVMe):
  - ESP (FAT32) montada em `/boot/efi`
  - ext4 `/boot`
  - root pretendido dentro de LUKS2 (btrfs)
- **Objetivo**: dual boot preservando Windows; root com LUKS2; snapshots btrfs depois

## Passos para reproduzir

1. Boot no live ISO do LMDE.
2. Criar partições:
   - manter a ESP existente (FAT32)
   - criar `/boot` em ext4
   - criar uma partição grande para criptografar (ex.: `/dev/nvme0n1p6`)
3. Desbloquear o alvo criptografado:

```bash
sudo cryptsetup luksFormat /dev/nvme0n1p6
sudo cryptsetup open /dev/nvme0n1p6 cryptroot
ls -la /dev/mapper/cryptroot
```

4. Abrir o instalador e ir para **Manual partitioning**.

## Esperado

- A UI lista **`/dev/mapper/cryptroot`** (ou equivalente) e permite selecioná-lo como `/` (e formatar como btrfs/ext4).

## Observado

- A UI **não lista** entradas `/dev/mapper/*`.
- Só aparece o device cru (`/dev/nvme0n1p6`) para seleção/formatação.
- Formatar `/dev/nvme0n1p6` quebra o header do LUKS e leva a loop de tentativa/erro e recuperação manual.

## Impacto

- Usuário fica entre uma opção insegura (formatar o device cru) e um workaround não óbvio.
- O caminho “particionamento manual” não é confiável para setups com dm-crypt/FDE.

## Workaround usado (funciona)

Instalar primeiro em **btrfs sem criptografia** na partição crua, **não reiniciar**, e depois criptografar “in-place” com `cryptsetup reencrypt`:

- Guia comunitário: `https://gist.github.com/Leniwcowaty/4b2c239ca74629cad60d4718f79ff600`

## Evidências úteis para anexar (sem dados sensíveis)

- Foto/print da tela de particionamento manual **sem** `/dev/mapper/*` listados.
- Saída de `ls -la /dev/mapper/` no Live, mostrando o mapper criado (ex.: `cryptroot`).
- Saída de `lsblk -f` antes de abrir o instalador (para mostrar que o mapper existe).

## Direção sugerida de correção

- No particionamento manual, atualizar a lista de dispositivos após o unlock do dm-crypt e incluir `/dev/mapper/*`.
- Alternativamente, oferecer uma ação explícita “desbloquear volume criptografado” e, uma vez desbloqueado, expor o mapper device na UI.

