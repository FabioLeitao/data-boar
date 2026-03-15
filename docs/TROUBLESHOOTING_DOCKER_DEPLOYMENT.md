# Troubleshooting: Docker deployment and container networking

**Português (Brasil):** [TROUBLESHOOTING_DOCKER_DEPLOYMENT.pt_BR.md](TROUBLESHOOTING_DOCKER_DEPLOYMENT.pt_BR.md)

**See also:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (overview and quick hints).

This document helps when Data Boar runs **inside a Docker container** and must connect to **remote databases**, **NFS/SMB shares**, or **APIs**. It covers network reachability from the container, DNS, and how to use host-mounted shares vs NFS/SMB targets.

---

## 1. Remote databases from inside the container

**Scenario:** Config has a database target (PostgreSQL, MySQL, etc.) but the scan fails with **unreachable** or connection refused.

### 1.1 Use hostname or IP that the container can resolve and reach

- **Do not** use `localhost` in config for a DB that runs on the **host** or another machine. From inside the container, `localhost` is the container itself.
- Use the **host’s IP** on the Docker bridge (e.g. `172.17.0.1` on default bridge) or the **hostname** of the DB server. On Docker Desktop (Windows/Mac), you can often use **`host.docker.internal`** as the DB host so the container reaches a service on the host.
- **Example:** DB on host, port 5432. Config: `host: host.docker.internal`, `port: 5432` (or use the host’s real IP). Ensure the DB server listens on an address the container can reach (e.g. `0.0.0.0` or the bridge IP), not only `127.0.0.1`.

### 1.2 Checklist

1. From the **host**, test: `psql -h <host> -p 5432 -U <user> -d <db>` (or equivalent). If it fails, fix DB and firewall on the host first.
1. From **inside the container**: `docker exec <container> sh -c 'command -v nc && nc -zv <db-host> <port>'` (or use a small image with `nc`/`curl`). If this fails, the container cannot reach the DB (network/DNS/firewall).
1. **DNS:** If config uses a hostname, the container must resolve it. Use the same DNS as the host (`--dns 8.8.8.8` or host’s DNS) or run with `--network host` (Linux) so the container shares the host’s network (and DNS).

### 1.3 Steps to fix

- Set `host` in config to an IP or hostname that the container can reach (`host.docker.internal` for host services on Docker Desktop; or the DB server’s FQDN/IP).
- Ensure the DB server allows connections from the container’s IP (or Docker bridge subnet).
- If resolution fails, fix container DNS (`--dns`) or use IP instead of hostname.

---

## 2. NFS or SMB from the container (two approaches)

**Scenario:** You want to scan files on an NFS or SMB share. Two common patterns:

### 2.1 Approach A: Mount the share on the host, bind-mount into the container (recommended when possible)

- **On the host:** Mount the NFS or SMB share (e.g. `/mnt/nfs-audit` or `C:\Mounts\SMBShare`).
- **Run the container** with a bind mount of that path, e.g. `-v /mnt/nfs-audit:/data/shared`.
- **In config:** Use a **filesystem** target with `path: /data/shared` (and optional `recursive: true`). No NFS/SMB target type needed; the app just reads files under that path.
- **Pros:** No need for NFS/SMB client inside the container; no extra firewall from container to NFS/SMB server. Works the same on Linux and Windows (host has the mount).
- **Cons:** The host must have the share mounted before starting the container; host must have NFS/SMB client tools.

### 2.2 Approach B: NFS/SMB target in config (container talks directly to the share)

- **In config:** Add a target with `type: nfs` or `type: smb` and the appropriate `host`, `path`, `share`, credentials, etc. (see [USAGE.md](USAGE.md) and [ADDING_CONNECTORS.md](ADDING_CONNECTORS.md)).
- **Image:** The image must include the optional **shares** extra (NFS/SMB client libraries). The pre-built image may or may not include it; if you get "smbprotocol not installed" or similar, build a custom image with `pip install -e ".[shares]"` (or use the image that documents shares support).
- **Network:** The **container** must be able to reach the NFS server (ports 2049, 111, etc.) or SMB server (445). Open outbound firewall from the container network to those ports; ensure DNS resolution if you use hostnames.
- **Pros:** No host mount; config is self-contained. Good when the container runs in a cluster and can reach the share directly.
- **Cons:** Requires correct container network and firewall; image must include shares support.

### 2.3 What to look for when it fails

- **"Missing host" / "Missing share name":** Fill in `host`, `share` (SMB), and path in config.
- **"unreachable":** Container cannot reach NFS/SMB server. Check firewall (outbound from container to server ports); test with `docker exec <container> nc -zv <server> 445` (SMB) or `2049` (NFS).
- **"smbprotocol not installed" (or NFS client missing):** Install optional dependency and rebuild image; see [TECH_GUIDE.md](TECH_GUIDE.md) and [USAGE.md](USAGE.md).
- **"auth_failed":** Wrong credentials for the share; see [TROUBLESHOOTING_CREDENTIALS_AND_AUTH.md](TROUBLESHOOTING_CREDENTIALS_AND_AUTH.md).

### 2.4 Steps to fix

- **Approach A:** Mount share on host; bind-mount into container; use filesystem target. Verify the path is readable inside the container (`docker exec <container> ls /data/shared`).
- **Approach B:** Ensure image has shares support; open firewall from container to NFS/SMB; fix host/share/path and credentials in config; re-run and check Scan failures sheet and audit log.

---

## 3. DNS from inside the container

- If config uses **hostnames** (DB host, API base_url, NFS/SMB server), the container must resolve them. By default the container may use the host’s DNS or a default gateway DNS.
- **Symptom:** "unreachable" or "name or service not known" with a hostname in Details.
- **Fix:** Run with `--dns <your-dns-ip>` (e.g. `8.8.8.8` or the corporate DNS), or use **IPs** in config instead of hostnames for testing. In Compose/Kubernetes, set `dns` in the service spec.

---

## 4. Volumes and config path

- Config must be available **inside** the container. Typical setup: host dir `./data` with `config.yaml` → mount as `-v "$(pwd)/data:/data"` and set `CONFIG_PATH=/data/config.yaml`.
- **sqlite_path** and **report.output_dir** should be under the mounted volume (e.g. `/data/audit_results.db`, `/data/reports`) so data persists and you can read reports from the host.
- If the app reports "config not found" or wrong targets, check that `CONFIG_PATH` points to the file inside the container and that the mount is correct (`docker exec <container> cat /data/config.yaml`).

---

## 5. Summary table

| Goal                              | Recommended approach                                                                                                                                            | Doc reference   |
| ------                            | ----------------------                                                                                                                                          | --------------- |
| Scan DB on host from container    | Use `host.docker.internal` (or host IP) as DB host; ensure DB listens and firewall allows container.                                                            | § 1             |
| Scan files on NFS/SMB             | A) Mount share on host, bind-mount into container, use filesystem target. B) Use NFS/SMB target in config; image with `.[shares]`; container network to server. | § 2             |
| Container cannot resolve hostname | Set `--dns` or use IP in config.                                                                                                                                | § 3             |
| Config or reports not found       | Mount volume at `/data`; set `CONFIG_PATH=/data/config.yaml`; set sqlite_path and report.output_dir under `/data`.                                              | § 4             |

---

**Documentation index:** [README.md](README.md) · [README.pt_BR.md](README.pt_BR.md). **Overview:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md). **Deploy:** [deploy/DEPLOY.md](deploy/DEPLOY.md).
