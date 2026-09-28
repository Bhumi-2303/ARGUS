# ==================================================================
# ARGUS — Hardened Multi-Stage Production Container
# ==================================================================

# --- Stage 1: Frontend Static Build ---
FROM node:22-slim AS frontend-builder

WORKDIR /web

COPY web/package.json web/package-lock.json* ./
RUN npm ci --legacy-peer-deps

COPY web/ ./
RUN npm run build

# --- Stage 2: Python Dependency Builder ---
FROM python:3.11-slim AS python-builder

WORKDIR /build

# Build dependencies for C-extensions (LightGBM, XGBoost, PyArrow)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ libgomp1 && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# --- Stage 3: Minimal Hardened Runtime (NO COMPILERS) ---
FROM python:3.11-slim AS runtime

# Install only essential runtime dynamic libraries and healthcheck tool
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 curl && \
    rm -rf /var/lib/apt/lists/*

# Create hardened non-root system user & group (UID/GID 10001)
RUN groupadd -r -g 10001 argusgroup && \
    useradd -r -u 10001 -g argusgroup -d /app -s /sbin/nologin argususer

WORKDIR /app

# Copy virtual environment from builder
COPY --from=python-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application modules and configurations
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY configs/ ./configs/
COPY artifacts/ ./artifacts/
COPY results/ ./results/
COPY data/ ./data/
COPY prompts/ ./prompts/

# Copy compiled frontend assets
COPY --from=frontend-builder /web/dist ./web/dist

# Harden ownership and permissions
RUN chown -R argususer:argusgroup /app && \
    chmod -R 550 /app && \
    chmod -R 770 /tmp

USER argususer:argusgroup

ENV ARGUS_MODE=demo \
    ARGUS_HOST=0.0.0.0 \
    ARGUS_PORT=8000 \
    PYTHONPATH=/app/src:/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "argus.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
