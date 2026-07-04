# ==================================================================
# ARGUS — Multi-stage Production Dockerfile
# ==================================================================
# Stage 1: Build dependencies
# Stage 2: Minimal runtime image
# ==================================================================

# --- Builder Stage ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency specification first for layer caching
COPY pyproject.toml ./

# Install Python dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# --- Frontend Builder Stage ---
FROM node:22-slim AS frontend-builder

WORKDIR /frontend

# Copy frontend package files for layer caching
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# --- Runtime Stage ---
FROM python:3.12-slim AS runtime

# Security: run as non-root user
RUN groupadd -r argus && useradd -r -g argus -d /app -s /sbin/nologin argus

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY src/ ./src/
COPY config/ ./config/

# Copy built frontend into static serving directory
COPY --from=frontend-builder /frontend/dist ./static/

# Create data directories
RUN mkdir -p /app/data /app/logs && \
    chown -R argus:argus /app

# Switch to non-root user
USER argus

# Environment defaults
ENV ARGUS_ENV=production \
    ARGUS_HOST=0.0.0.0 \
    ARGUS_PORT=8000 \
    ARGUS_LOG_LEVEL=INFO \
    ARGUS_SQLITE_PATH=/app/data/argus.db \
    ARGUS_CHROMADB_PATH=/app/data/chromadb \
    PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8000/api/v1/health/live'); r.raise_for_status()" || exit 1

# Start the application
CMD ["uvicorn", "argus.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
