FROM python:3.11-slim

WORKDIR /app


# Install only the dependencies this service needs
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "kafka-python-ng>=2.2.0" \
        "pandas>=2.2.0" \
        "requests>=2.31.0" \
        "fastapi[standard]>=0.115.0" \
        "uvicorn[standard]>=0.30.0"

# Copy source code
COPY src/ ./src/

# Copy config
COPY config/ ./config/

# Environment variables for Docker container communication
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV KAFKA_TOPIC=argus-flows
ENV ORCHESTRATOR_API_URL=http://orchestrator:8004/process_alert
ENV PYTHONPATH=/app/src
RUN groupadd -r argus && useradd -r -g argus argus && chown -R argus:argus /app

# Default command: run stream consumer worker
USER argus
CMD ["python", "-m", "argus.services.streaming.stream_consumer"]
