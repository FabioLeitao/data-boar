# Portátil Windows: mais distros WSL e matriz de lab

**Objetivo:** Usar **um** PC com **Windows** como **vários** ambientes tipo Linux (**WSL2**) para repetir [HOMELAB_VALIDATION.md §9](HOMELAB_VALIDATION.md#9-multi-host-linux-optional-matrix-dns-ssh-different-distros) **sem** hardware extra — se **disco**, **RAM** e **CPU** aguentarem.

**Três portáteis (visão do operador):** (1) **Windows + WSL** (dev), (2) **Linux nativo** (ex. Zorin no Latitude), (3) **opcional** (ex. Lenovo guardado).

**Documento completo (EN):** [WINDOWS_WSL_MULTI_DISTRO_LAB.md](WINDOWS_WSL_MULTI_DISTRO_LAB.md)

**Resumo:** Já conta **Debian WSL2** + **Docker Desktop**; distros extra (ex. **Ubuntu-24.04**) custam **VHDX + RAM**. Limite com **`%UserProfile%\.wslconfig`**. Script: `pwsh -File scripts/windows-dev-report.ps1` (inclui **vswhere** com **`-prerelease`** para **Visual Studio Insiders**). O produto continua **Python**; Go/Rust/etc. são **opcionais**.
