# LGPD/GDPR/CCPA audit app – API mode. Python 3.12, non-root user, /data for config + DB + reports.
FROM python:3.12-slim

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

# API mode only; override CMD for one-shot CLI (e.g. docker run ... python main.py --config /data/config.yaml).
CMD ["python", "main.py", "--config", "/data/config.yaml", "--web", "--port", "8088"]
