# LGPD/GDPR/CCPA audit app. Default: web API + frontend (dashboard, reports, config UI).
# Override CMD to run CLI one-shot scan (see docs/deploy/DEPLOY.md).
# Multi-stage build: compile in builder, run in minimal runtime (no gcc/-dev in final image).

# -----------------------------------------------------------------------------
# Stage 1: build Python extensions and install dependencies
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ pkg-config \
    libpq-dev libffi-dev libssl-dev unixodbc-dev default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt

# Upgrade pip/wheel in builder before deps (Scout: pip<25.3, wheel<=0.46.1 had CVEs; image inherits site-packages).
RUN pip install --no-cache-dir --upgrade "pip>=25.3" "wheel>=0.46.2" && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    find /usr/local/lib/python3.12/site-packages -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
    find /usr/local/lib/python3.12/site-packages -name "*.pyc" -delete 2>/dev/null; true

# -----------------------------------------------------------------------------
# Stage 2: minimal runtime (no build tools, only runtime libs + app)
# -----------------------------------------------------------------------------
FROM python:3.12-slim

LABEL org.opencontainers.image.description="LGPD/GDPR/CCPA audit. Default: web API and frontend on port 8088. Override command for CLI one-shot."

# Runtime libs only (no -dev, no build-essential). Required by compiled wheels:
# libpq5=PostgreSQL, libffi8=cffi/cryptography, unixodbc=pyodbc, libmariadb3=mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libffi8 unixodbc libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder (no gcc/dev in this image)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Re-assert pip/wheel in the runtime layer so Docker Scout does not flag stale tooling copied from
# older builder caches (CVEs on wheel<=0.46.1, pip<25.3). App deps already live under site-packages.
RUN pip install --no-cache-dir --upgrade "pip>=25.3" "wheel>=0.46.2"

# Copy application code
COPY . .

ENV CONFIG_PATH=/data/config.yaml
ENV PYTHONUNBUFFERED=1

RUN useradd -r -u 1000 -d /data appuser && \
    mkdir -p /data && chown -R appuser:appuser /data

USER appuser

EXPOSE 8088

# Default: web API and frontend. CLI one-shot: override with --entrypoint python and args.
CMD ["python", "main.py", "--config", "/data/config.yaml", "--web", "--port", "8088"]
