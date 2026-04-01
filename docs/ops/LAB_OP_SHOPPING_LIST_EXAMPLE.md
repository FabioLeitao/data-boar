# Lab-op shopping list (example, tracked)

This is a **public, tracked** example shopping list that demonstrates how we structure hardware planning **without** leaking operator-specific pricing, store links, CEP/location hints, serials, or home/lab identifiers.

## Principles

- **Track categories and rationale**, not live prices.
- **Prefer compatibility facts** (DDR generation, voltage, speed, rank) over “best deal” links.
- Keep the **real** shopping plan in `docs/private/` (gitignored).

## Example: RAM upgrade planning (generic)

### Identify your target

- **Laptop model**: ThinkPad *WORKSTATION* / *LAB-NODE-01* (exact generation matters)
- **Goal**: e.g. 16→32 GiB, 16→64 GiB, dual-channel, low-power idle, stability

### Checklist to collect before buying

- Current RAM layout: 1× or 2× modules, soldered + slot, max supported
- DDR generation (DDR4 vs DDR5)
- SODIMM vs soldered-only (varies by generation)
- Speed target: match the platform default (avoid overpaying for clocks you can’t use)
- Voltage and JEDEC profile (avoid “XMP-only” kits for laptops)

### Example bill of materials (no prices)

- **RAM**: 2×16 GiB or 2×32 GiB SODIMM kit (JEDEC, laptop-friendly)
- **Tools**: small Phillips, spudger, ESD strap (optional), tray for screws
- **Validation**: `memtest86+` / `memtester`, and a short stress run after install

## Where the real plan lives

- Private cover note (tracked): `docs/private.example/homelab/LAB_OP_SHOPPING_LIST_COVER_NOTE.md`
- Real list (gitignored): `docs/private/homelab/LAB_OP_SHOPPING_LIST_AND_POWER.md`

