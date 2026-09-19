# ==================================================================
# ARGUS — Multi-stage Production Dockerfile
# ==================================================================

# --- Builder Stage ---
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ ./src/

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# --- Frontend Builder Stage ---
FROM node:22-slim AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- Runtime Stage ---
FROM python:3.11-slim AS runtime

RUN groupadd -r argus && useradd -r -g argus -d /app -s /sbin/nologin argus

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY src/ ./src/
COPY config/ ./config/
COPY --from=frontend-builder /frontend/dist ./static/

RUN mkdir -p /app/data /app/logs && \
    chown -R argus:argus /app

USER argus

ENV ARGUS_ENV=production \
    ARGUS_HOST=0.0.0.0 \
    ARGUS_PORT=8000 \
    ARGUS_LOG_LEVEL=INFO \
    ARGUS_SQLITE_PATH=/app/data/argus.db \
    ARGUS_CHROMADB_PATH=/app/data/chromadb \
    PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "argus.services.detector.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
