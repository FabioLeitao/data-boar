# Draft: LMDE installer manual partitioning hides dm-crypt (`/dev/mapper/*`)

This is a **draft** you can paste into a bug tracker for the LMDE/Linux Mint installer (Ubiquity / partitioning UI). It intentionally avoids secrets and environment-specific LAN details.

## Where to report

- Primary: open an issue in `linuxmint/ubiquity` (GitHub).
- Guidance: `https://linuxmint.github.io/reporting-an-issue.html` (general Mint/Cinnamon reporting rules; applies to choosing the right project and writing reproducible steps).

## Summary

When installing **LMDE** with **manual partitioning**, unlocked **dm-crypt** devices (e.g. `cryptsetup open … cryptroot` → `/dev/mapper/cryptroot`) are **not shown** in the partition list, so the installer cannot select them as `/`.

This leads users to accidentally select the underlying block device (e.g. `/dev/nvme0n1p6`) and format it, which destroys the LUKS header and breaks the intended full-disk encryption flow.

## Environment

- **Distro / installer**: LMDE 7 “Gigi” live ISO (installer “Install Linux Mint” / manual partitioning UI)
- **Firmware**: UEFI, Secure Boot enabled
- **Disk layout** (single NVMe):
  - ESP (FAT32) mounted at `/boot/efi`
  - ext4 `/boot`
  - root intended inside LUKS2 (btrfs)
- **Goal**: dual boot with Windows preserved; root encrypted with LUKS2; btrfs snapshots later

## Repro steps

1. Boot LMDE live ISO.
2. Create partitions:
   - keep existing ESP (FAT32)
   - create ext4 `/boot`
   - create a large partition to be encrypted (e.g. `/dev/nvme0n1p6`)
3. Unlock the intended encrypted target:

```bash
sudo cryptsetup luksFormat /dev/nvme0n1p6
sudo cryptsetup open /dev/nvme0n1p6 cryptroot
ls -la /dev/mapper/cryptroot
```

4. Start the installer and go to **Manual partitioning**.

## Expected

- The partitioning UI lists **`/dev/mapper/cryptroot`** (or equivalent) and allows selecting it as the mount point `/` (and formatting it as btrfs/ext4).

## Actual

- The UI does **not** list `/dev/mapper/*` entries.
- Only the underlying block device (`/dev/nvme0n1p6`) is available for selection/formatting.
- Formatting `/dev/nvme0n1p6` breaks the LUKS header and causes a loop of failed installs / manual recovery attempts.

## Impact

- Users are pushed into an unsafe choice (formatting the raw device) or into a non-obvious workaround.
- The “manual partitioning” path is not reliable for dm-crypt/FDE setups.

## Workaround used (works)

Install first on **plain btrfs** on the raw partition, **do not reboot**, then encrypt in-place using `cryptsetup reencrypt` (Mint-like FDE flow):

- Community guide: `https://gist.github.com/Leniwcowaty/4b2c239ca74629cad60d4718f79ff600`

## Evidence worth attaching (non-sensitive)

- Screenshot of the manual partitioning screen **without** any `/dev/mapper/*` entries.
- Output of `ls -la /dev/mapper/` in the live session showing the unlocked mapping (e.g. `cryptroot`).
- Output of `lsblk -f` right before launching the installer (to show the mapper exists).

## Suggested fix direction

- In manual partitioning, refresh the device list after dm-crypt unlock and include `/dev/mapper/*` devices.
- Alternatively, provide an explicit “unlock encrypted volume” action in the UI and surface the mapper device once unlocked.

