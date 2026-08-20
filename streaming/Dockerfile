FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY streaming/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy streaming scripts
COPY streaming/stream_consumer.py /app/streaming/stream_consumer.py
COPY streaming/replay_producer.py /app/streaming/replay_producer.py

# Environment variables for Docker container communication
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV KAFKA_TOPIC=argus-flows
ENV ORCHESTRATOR_API_URL=http://orchestrator:8004/process_alert
ENV PYTHONPATH=/app

# Default command: run stream consumer worker
CMD ["python", "streaming/stream_consumer.py"]
