# ==================================================================
# ARGUS — Multi-stage Production & Air-Gapped OT Dockerfile
# ==================================================================

# --- Stage 1: Frontend Builder ---
FROM node:22-slim AS frontend-builder

WORKDIR /web

# Copy package manifests and install dependencies
COPY web/package.json web/package-lock.json* ./
RUN npm ci --legacy-peer-deps

# Copy frontend source and compile production static bundle
COPY web/ ./
RUN npm run build

# --- Stage 2: Production Backend Runtime ---
FROM python:3.11-slim AS runtime

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libgomp1 curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for container security hardening
RUN groupadd -r argusgroup && useradd -r -g argusgroup -d /app -s /sbin/nologin argususer

WORKDIR /app

# Copy python dependencies and source code
COPY pyproject.toml ./
COPY src/ ./src/

# Install python package and dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy authoritative model artifacts, verified results, sample parquets, and prompts
COPY artifacts/ ./artifacts/
COPY results/ ./results/
COPY data/ ./data/
COPY prompts/ ./prompts/

# Copy compiled frontend static assets from Stage 1
COPY --from=frontend-builder /web/dist ./web/dist

# Set permissions for non-root user
RUN chown -R argususer:argusgroup /app

USER argususer

# Environment Variable Defaults
ENV ARGUS_MODE=demo \
    ARGUS_HOST=0.0.0.0 \
    ARGUS_PORT=8000 \
    PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Container Healthcheck hitting /health endpoint
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch FastAPI app with Uvicorn
CMD ["uvicorn", "argus.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
