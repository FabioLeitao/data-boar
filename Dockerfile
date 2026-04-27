# LGPD/GDPR/CCPA audit app. Default: web API + frontend (dashboard, reports, config UI).
# Override CMD to run CLI one-shot scan (see docs/deploy/DEPLOY.md).
#
# Hardening posture (see docs/adr/0044-container-image-hardening-databoar-user.md):
#   - Multi-stage build keeps gcc / -dev / build-essential out of the final image.
#   - Final image runs as a dedicated, non-root `databoar` user (uid 1000).
#   - Package managers (pip, wheel) are removed from the runtime stage so Docker
#     Scout has nothing left to flag and an attacker cannot `pip install` payloads.
#   - PYTHONDONTWRITEBYTECODE keeps the runtime filesystem clean so Compose
#     `read_only: true` works without tmpfs noise outside /tmp and /data.
#   - HEALTHCHECK is declared in the image so plain `docker run` (no Compose)
#     still surfaces liveness through `docker ps`.
#
# This is image hardening only — ZERO change to connector / sampling SQL paths.
# Defensive Scanning Manifesto (docs/ops/inspirations/) still owns those.

# -----------------------------------------------------------------------------
# Stage 1: build Python extensions and install dependencies
# -----------------------------------------------------------------------------
# Rolling 3.13 slim: aligns with CI (3.12 + 3.13), requires-python >=3.12, and
# Docker Scout base-image recommendations (fewer base CVEs vs. 3.12-slim).
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ pkg-config \
    libpq-dev libffi-dev libssl-dev unixodbc-dev default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
# `requirements.txt` begins with `-e .` (uv export); pip needs the project tree at /app before `pip install -r`.
COPY . /app

# Upgrade pip/wheel in builder before deps (Scout: pip<25.3, wheel<=0.46.1 had CVEs).
# `uv export` emits `-e .` plus hashed wheels; pip refuses editable + hashes in one
# `install -r` pass — split installs.
# Do not end this RUN with `; true` — it would mask a failed `pip install`.
RUN pip uninstall -y wheel || true && \
    pip install --no-cache-dir --upgrade "pip>=25.3" && \
    pip install --no-cache-dir --force-reinstall "wheel>=0.46.2" && \
    python -c "import wheel; import sys; sys.exit(0 if tuple(map(int, wheel.__version__.split('.'))) >= (0,46,2) else 1)" && \
    python -c "from pathlib import Path; s=Path('/app/requirements.txt').read_text(encoding='utf-8').splitlines(); Path('/app/requirements.docker.txt').write_text('\\n'.join(x for x in s if x.strip()!='-e .')+'\\n', encoding='utf-8')" && \
    pip install --no-cache-dir -r /app/requirements.docker.txt && \
    pip install --no-cache-dir --no-deps -e /app && \
    (find /usr/local/lib/python3.13/site-packages -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true) && \
    (find /usr/local/lib/python3.13/site-packages -name "*.pyc" -delete 2>/dev/null || true)

# -----------------------------------------------------------------------------
# Stage 2: minimal runtime (no build tools, no package managers, app-only)
# -----------------------------------------------------------------------------
FROM python:3.13-slim

# OCI image labels — populated by docker buildx / docker-lab-build.ps1 at build time
# but with sensible defaults so plain `docker build` still produces labeled images.
ARG DATA_BOAR_VERSION=dev
ARG VCS_REF=unknown
ARG BUILD_DATE=unknown

LABEL org.opencontainers.image.title="Data Boar" \
      org.opencontainers.image.description="LGPD/GDPR/CCPA audit. Default: web API and frontend on port 8088. Override command for CLI one-shot." \
      org.opencontainers.image.vendor="Fabio Leitao" \
      org.opencontainers.image.source="https://github.com/FabioLeitao/data-boar" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="${DATA_BOAR_VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.created="${BUILD_DATE}"

# Runtime libs only (no -dev, no build-essential). Required by compiled wheels:
# libpq5=PostgreSQL, libffi8=cffi/cryptography, unixodbc=pyodbc, libmariadb3=mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libffi8 unixodbc libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

# Optional rich media (not installed by default — keeps image small): if you set
# file_scan.scan_image_ocr or need ffprobe for video tags, extend this stage with e.g.
# tesseract-ocr, tesseract-ocr-eng, ffmpeg (provides ffprobe), and pip install ".[richmedia]".

WORKDIR /app

# Copy installed packages and entrypoints from builder (no gcc / no -dev in final image)
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Attack-surface reduction: remove pip + wheel from the runtime image.
# We already installed all dependencies in the builder stage; the final image
# has no reason to keep a package manager around. Removing the binaries AND the
# site-packages directories is what eliminates Docker Scout pip/wheel CVE noise
# (instead of an "upgrade-then-leave-it" cycle that re-introduces fresh CVEs).
# setuptools is kept because some packages still query pkg_resources at import time.
RUN rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.13 \
          /usr/local/bin/wheel && \
    find /usr/local/lib/python3.13/site-packages -maxdepth 1 \
         \( -name "pip" -o -name "pip-*" -o -name "wheel" -o -name "wheel-*" \) \
         -exec rm -rf {} + 2>/dev/null || true

# Copy application code
COPY . .

ENV CONFIG_PATH=/data/config.yaml \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    API_HOST=0.0.0.0

# Dedicated non-root user (uid:gid 1000:1000). Name change appuser -> databoar
# is intentional: Compose / k8s manifests can pin `user: "1000:1000"` regardless.
RUN groupadd -r -g 1000 databoar && \
    useradd -r -u 1000 -g 1000 -d /data -s /sbin/nologin databoar && \
    mkdir -p /data && chown -R databoar:databoar /data /app

USER databoar

EXPOSE 8088

# Image-level healthcheck — works for plain `docker run` too.
# Compose may override; keeping it here avoids "no health" when the override is omitted.
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8088/health')"]

# Default: web API and frontend. CLI one-shot: override with --entrypoint python and args.
# Plaintext HTTP with explicit opt-in (mount TLS cert/key and drop this flag for HTTPS).
CMD ["python", "main.py", "--config", "/data/config.yaml", "--web", "--port", "8088", "--allow-insecure-http"]
