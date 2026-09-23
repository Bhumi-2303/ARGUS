FROM python:3.11-slim

WORKDIR /app


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install only the dependencies this service needs (fast, no torch/google-adk)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "fastapi[standard]>=0.115.0" \
        "uvicorn[standard]>=0.30.0" \
        "pydantic>=2.7.0" \
        "lightgbm>=4.3.0" \
        "shap>=0.45.0" \
        "numpy>=1.26.0" \
        "pandas>=2.2.0"

# Copy source code
COPY src/ ./src/

# Copy config files
COPY config/ ./config/

# Set environment configuration
ENV MODEL_PATH=/app/models/model_d2_coral.txt
ENV THRESHOLD=0.50
ENV PYTHONPATH=/app/src
RUN groupadd -r argus && useradd -r -g argus argus && chown -R argus:argus /app

USER argus
EXPOSE 8000

# Start Uvicorn server
CMD ["uvicorn", "argus.services.detector.main:app", "--host", "0.0.0.0", "--port", "8000"]
