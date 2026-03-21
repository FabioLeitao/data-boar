# UniFi Dream Machine SE — lab VLANs, firewall, and SNMP (before a monitoring server)

**Purpose:** Use your **UniFi Dream Machine SE (UDM-SE)** for **isolated lab traffic** and **early SNMP visibility** while the **Proxmox / monitoring host** is not ready yet.

**Important:** Neither this repository nor an AI assistant can **poll or configure** your UDM-SE over the internet unless **you** expose management (not recommended). All SNMP and UniFi UI steps run **on your LAN** from **your** workstation or a temporary Linux host.

**Official SNMP reference:** [SNMP Monitoring in UniFi Network](https://help.ui.com/hc/en-us/articles/33502980942615-SNMP-Monitoring-in-UniFi-Network) (Ubiquiti Help Center).

---

## 1. Can “we” gather SNMP before the monitoring server exists?

**Yes — you can, locally.** The monitoring **server** (Zabbix, Prometheus SNMP exporter, LibreNMS, etc.) is optional for a **first check**.

1. **Enable SNMP** on UniFi: **Settings → CyberSecure → Traffic Logging** (per Ubiquiti; menu names can shift slightly with UniFi OS updates—search Help Center if moved).
1. Prefer **SNMPv3** (user + auth/priv passwords) over **v2c community** on a home/lab network that may have Wi‑Fi guests.
1. From any **Linux** machine on the same reachable segment as the gateway (e.g. your Zorin laptop, or a small Proxmox VM later), install **Net-SNMP** client tools and run **`snmpwalk`** against the **UDM-SE management IP** (usually the gateway on your main LAN, or a dedicated **management VLAN** if you use one).

## Example (illustrative — replace user, auth, IP):

```bash
# Debian/Ubuntu: sudo apt install -y snmp snmp-mibs-downloader
# May need: export MIBS=ALL

snmpwalk -v3 -l authPriv -u YOUR_V3_USER -a SHA -A 'AUTH_PASS' -x AES -X 'PRIV_PASS' UDM_SE_IP 1.3.6.1.2.1.2.2
```

The OID `1.3.6.1.2.1.2.2` is the standard **interfaces** table (traffic counters per interface index). Upload Ubiquiti’s **UI-MIB** (linked from the Help article) into your future NMS for readable names; **`snmpwalk` without MIBs** still returns numeric OIDs.

**Firewall:** Allow **UDP 161** from **only** the host(s) that poll (your laptop IP, or a future monitoring VM). **Do not** expose SNMP to the **WAN** or to untrusted VLANs.

**Limits:** Ubiquiti notes **SNMP traps** are not fully there yet (check current release notes). Polling is still enough for **interface octets**, basic health, and “is the pipe full?” before Grafana/Loki/etc. land on the tower.

---

## 2. VLANs and rules for homelab / Data Boar testing

Use VLANs to **separate** roles without putting **real VLAN IDs, subnet names, or passwords** in this public repo—keep those in **`docs/private/homelab/`** (gitignored) or your runbook ([PRIVATE_OPERATOR_NOTES.md](../PRIVATE_OPERATOR_NOTES.md)).

## Typical pattern (names are examples only):

| VLAN role (example) | Use                                                                                 |
| ------------------- | ---                                                                                 |
| **Trusted LAN**     | Desktops, daily use, UniFi management (or restrict management to a dedicated VLAN). |
| **Lab / servers**   | Proxmox host, Linux VMs, Docker/K8s nodes, synthetic DB containers.                 |
| **IoT / guest**     | No routing to lab subnets by default; no SNMP to gateway from here.                 |

## Firewall (UniFi):

- **Default deny** from **guest/IoT → lab**.
- Allow **your workstation → lab** only on ports you need (e.g. **8088** for Data Boar dashboard during tests, **22** for SSH if policy allows).
- If you want to **simulate** “strict corporate” paths: add a rule that **blocks** something Data Boar needs (e.g. DB port) and confirm **scan failures** and **recommendations** in reports match expectations—**document the scenario** in private notes.

**Data Boar note:** The app does not need UniFi-specific config; it follows **IP/DNS + ports** in `config.yaml`. VLANs only change **which paths** are allowed.

---

## 3. Traffic “checking” without full NMS

Until Prometheus/Grafana (or similar) runs on the **future server**:

- **UniFi Network UI:** Traffic charts, client history, and per-device stats are often enough for **who is noisy** and **WAN usage**.
- **SNMP polling from laptop:** Script a cron job or manual **`snmpwalk`** to a file for **before/after** comparisons during heavy scans.
- **tcpdump / Wireshark** on a **mirrored port** or on the **scanning host** (with policy)—for deep dives, not daily.

---

## 4. What to send if you want design feedback (text only)

- **Goal:** e.g. “isolate Proxmox + DB containers from Wi‑Fi” or “test blocked DB port.”
- **Rough topology:** “UDM-SE → switch → one trunk with VLANs X/Y” (use **placeholders** in chat if public).
- **Whether SNMP is enabled** and **v2c vs v3**.

We can suggest **rule ordering** and **test ideas** in text; we cannot apply settings to your controller.

---

## 5. See also

- [HOMELAB_VALIDATION.md](HOMELAB_VALIDATION.md) — multi-host matrix; keep LAN details private.
- [HOMELAB_POWER_AND_ELECTRICAL_PLANNING.md](HOMELAB_POWER_AND_ELECTRICAL_PLANNING.md) — AC + breaker planning; **§5.2** UniFi **SmartPower (USP-RPS)** vs **second nobreak** to **free watts** on your main UPS.
- [SECURITY.md](../../SECURITY.md) — binding, API keys, least exposure.

**Português (Brasil):** [HOMELAB_UNIFI_UDM_LAB_NETWORK.pt_BR.md](HOMELAB_UNIFI_UDM_LAB_NETWORK.pt_BR.md)
