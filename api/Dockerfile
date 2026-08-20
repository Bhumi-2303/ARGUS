FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code and trained model file
COPY api/main.py /app/api/main.py
COPY phase3_results/models/model_d2_coral.txt /app/phase3_results/models/model_d2_coral.txt

# Set environment configuration
ENV MODEL_PATH=/app/phase3_results/models/model_d2_coral.txt
ENV THRESHOLD=0.50
ENV PYTHONPATH=/app

EXPOSE 8000

# Start Uvicorn server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
