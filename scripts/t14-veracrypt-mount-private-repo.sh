#!/usr/bin/env bash
# Mount the private_repo.vc hidden volume (PIM + keyfile + password prompt).
# Hash (e.g. SHA-512) is fixed when the volume was created; it is not passed at mount time.
# Defaults match VERACRYPT_PRIVATE_REPO_SETUP.pt_BR.md section 6.4 (paths under $HOME).
#
# Usage (on T14, after veracrypt CLI is installed):
#   chmod 600 ~/.kb-private/keyfile.bin   # once
#   bash scripts/t14-veracrypt-mount-private-repo.sh
#
# Override: MNT=/mnt/private PIM=485 VC_PATH=... KEYFILE=...
set -eu

VC_PATH="${VC_PATH:-${HOME}/.kb-cache/private_repo.vc}"
KEYFILE="${KEYFILE:-${HOME}/.kb-private/keyfile.bin}"
MNT="${MNT:-/mnt/private}"
PIM="${PIM:-485}"

if ! command -v veracrypt >/dev/null 2>&1; then
  echo "veracrypt not in PATH. Install first: bash scripts/t14-install-veracrypt-console-debian13.sh"
  exit 1
fi
if [[ ! -f "${VC_PATH}" ]]; then
  echo "Missing container: ${VC_PATH}"
  exit 1
fi
if [[ ! -f "${KEYFILE}" ]]; then
  echo "Missing keyfile: ${KEYFILE}"
  exit 1
fi

chmod 600 "${KEYFILE}" 2>/dev/null || true

echo "==> Prepare mount point ${MNT}"
sudo mkdir -p "${MNT}"
sudo chown "$(id -u):$(id -g)" "${MNT}"

echo "==> Mount (hidden volume): you will be prompted for the hidden-volume password"
echo "    Container: ${VC_PATH}"
echo "    Keyfile:   ${KEYFILE}"
echo "    PIM:       ${PIM}"
# --protect-hidden=no: allow mounting hidden when required (see VeraCrypt CLI help on your version)
veracrypt --mount "${VC_PATH}" "${MNT}" \
  --keyfiles "${KEYFILE}" \
  --pim="${PIM}" \
  --protect-hidden=no

echo "==> OK. Try: ls ${MNT}  and  git -C ${MNT}/working status"
echo "    Dismount example: veracrypt --dismount ${MNT}"
