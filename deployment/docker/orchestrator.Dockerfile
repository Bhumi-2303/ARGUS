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

# Copy config
COPY config/ ./config/

# Microservice URLs configuration
ENV DETECTOR_API_URL=http://detector-api:8000/predict
ENV RISK_API_URL=http://risk-agent:8002/risk_score
ENV KNOWLEDGE_API_URL=http://knowledge-agent:8003/context
ENV DECISION_API_URL=http://decision-agent:8001/explain
ENV PYTHONPATH=/app/src
RUN groupadd -r argus && useradd -r -g argus argus && chown -R argus:argus /app

USER argus
EXPOSE 8004

CMD ["uvicorn", "argus.services.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8004"]
