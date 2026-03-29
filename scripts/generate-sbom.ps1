#Requires -Version 5.1
<#
.SYNOPSIS
  Generate CycloneDX SBOMs per ADR 0003 (Python from lockfile export, then Syft on a local image).

.DESCRIPTION
  Mirrors the logic in `.github/workflows/sbom.yml`. Outputs:
  - `sbom-python.cdx.json` — CycloneDX 1.6 JSON from `uv export` + `cyclonedx-py`.
  - `sbom-docker-image.cdx.json` — Syft in `anchore/syft:v1.28.0` against `data_boar:sbom`.

  The Syft step expects Docker to reach the daemon (Linux, macOS, or Docker Desktop with a
  Linux engine). If `docker run` with a Unix socket fails on your host, use the CI workflow
  artifacts instead.

.NOTES
  Run from repo root: `.\scripts\generate-sbom.ps1`
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

Write-Host "==> uv sync --group dev"
uv sync --group dev

Write-Host "==> uv export -> requirements-sbom.txt"
uv export --no-emit-package pyproject.toml -o requirements-sbom.txt

Write-Host "==> CycloneDX (Python)"
uv run cyclonedx-py requirements requirements-sbom.txt `
    --pyproject pyproject.toml `
    --sv 1.6 `
    --of JSON `
    --output-reproducible `
    -o sbom-python.cdx.json

Write-Host "==> docker build -> data_boar:sbom"
docker build -t data_boar:sbom -f Dockerfile .

Write-Host "==> Syft (image SBOM)"
$outPath = (Get-Location).Path
docker run --rm `
    -v "/var/run/docker.sock:/var/run/docker.sock" `
    -v "${outPath}:/out" `
    anchore/syft:v1.28.0 `
    scan docker:data_boar:sbom `
    -o cyclonedx-json=/out/sbom-docker-image.cdx.json

Write-Host "Done: sbom-python.cdx.json, sbom-docker-image.cdx.json"
