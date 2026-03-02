# LGPD/GDPR/CCPA audit app. Default: web API + frontend (dashboard, reports, config UI).
# Override CMD to run CLI one-shot scan (see deploy/DEPLOY.md).
FROM python:3.12-slim

LABEL org.opencontainers.image.description="LGPD/GDPR/CCPA audit. Default: web API and frontend on port 8088. Override command for CLI one-shot."

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libffi7 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Default: config and persistent data under /data (mount as volume).
ENV CONFIG_PATH=/data/config.yaml
ENV PYTHONUNBUFFERED=1

RUN useradd -r -u 1000 -d /data appuser && \
    mkdir -p /data && chown -R appuser:appuser /data

USER appuser

EXPOSE 8088

# Default: web API and frontend (dashboard, reports, config). No command override in Compose/Kubernetes = this runs.
# CLI one-shot: docker run ... --entrypoint python IMAGE main.py --config /data/config.yaml [--tenant X --technician Y]
CMD ["python", "main.py", "--config", "/data/config.yaml", "--web", "--port", "8088"]
