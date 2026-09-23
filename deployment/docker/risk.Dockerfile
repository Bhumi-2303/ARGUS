FROM python:3.11-slim

WORKDIR /app


# Install only the dependencies this service needs
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "fastapi[standard]>=0.115.0" \
        "uvicorn[standard]>=0.30.0" \
        "pydantic>=2.7.0" \
        "requests>=2.31.0"

# Copy source code
COPY src/ ./src/

# Copy config and asset inventory
COPY config/ ./config/
COPY risk_agent/asset_inventory.json ./risk_agent/asset_inventory.json

# Environment variables
ENV DETECTOR_API_URL=http://detector-api:8000/predict
ENV INVENTORY_PATH=/app/risk_agent/asset_inventory.json
ENV WEIGHT_PROBABILITY=0.60
ENV WEIGHT_CRITICALITY=0.40
ENV PYTHONPATH=/app/src
RUN groupadd -r argus && useradd -r -g argus argus && chown -R argus:argus /app

USER argus
EXPOSE 8002

CMD ["uvicorn", "argus.services.risk_agent.main:app", "--host", "0.0.0.0", "--port", "8002"]
