FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY risk_agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code and synthetic asset inventory JSON
COPY risk_agent/main.py /app/risk_agent/main.py
COPY risk_agent/asset_inventory.json /app/risk_agent/asset_inventory.json

# Environment variables
ENV DETECTOR_API_URL=http://detector-api:8000/predict
ENV INVENTORY_PATH=/app/risk_agent/asset_inventory.json
ENV WEIGHT_PROBABILITY=0.60
ENV WEIGHT_CRITICALITY=0.40
ENV PYTHONPATH=/app

EXPOSE 8002

# Start Uvicorn server
CMD ["uvicorn", "risk_agent.main:app", "--host", "0.0.0.0", "--port", "8002"]
