FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY knowledge_agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code and persistent Chroma DB
COPY knowledge_agent/main.py /app/knowledge_agent/main.py
COPY knowledge_agent/chroma_db /app/knowledge_agent/chroma_db

# Environment variables
ENV CHROMA_DB_DIR=/app/knowledge_agent/chroma_db
ENV COLLECTION_NAME=mitre_attack_ics
ENV EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV PYTHONPATH=/app

EXPOSE 8003

# Start Uvicorn server
CMD ["uvicorn", "knowledge_agent.main:app", "--host", "0.0.0.0", "--port", "8003"]
