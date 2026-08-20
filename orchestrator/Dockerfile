FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY orchestrator/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY orchestrator/main.py /app/orchestrator/main.py

# Microservice URLs configuration
ENV DETECTOR_API_URL=http://detector-api:8000/predict
ENV RISK_API_URL=http://risk-agent:8002/risk_score
ENV KNOWLEDGE_API_URL=http://knowledge-agent:8003/context
ENV DECISION_API_URL=http://decision-agent:8001/explain
ENV PYTHONPATH=/app

EXPOSE 8004

# Start Uvicorn server
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8004"]
