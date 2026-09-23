FROM python:3.11-slim

WORKDIR /app


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install only the dependencies this service needs
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "fastapi[standard]>=0.115.0" \
        "uvicorn[standard]>=0.30.0" \
        "pydantic>=2.7.0" \
        "chromadb>=0.5.0" \
        "sentence-transformers>=3.0.0" \
        "requests>=2.31.0"

# Copy source code
COPY src/ ./src/

# Copy config and persistent Chroma DB
COPY config/ ./config/
COPY knowledge_agent/chroma_db ./knowledge_agent/chroma_db

# Environment variables
ENV CHROMA_DB_DIR=/app/knowledge_agent/chroma_db
ENV COLLECTION_NAME=mitre_attack_ics
ENV EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV PYTHONPATH=/app/src
RUN groupadd -r argus && useradd -r -g argus argus && chown -R argus:argus /app

USER argus
EXPOSE 8003

CMD ["uvicorn", "argus.services.knowledge_agent.main:app", "--host", "0.0.0.0", "--port", "8003"]
