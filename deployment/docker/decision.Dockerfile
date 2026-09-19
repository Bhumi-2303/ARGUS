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

# Copy config and prompt files
COPY config/ ./config/
COPY prompts/decision_support_system_prompt.txt ./prompts/decision_support_system_prompt.txt

# Environment variables
ENV DETECTOR_API_URL=http://detector-api:8000/predict
ENV OLLAMA_API_URL=http://ollama:11434
ENV OLLAMA_MODEL=llama3.2
ENV PROMPT_PATH=/app/prompts/decision_support_system_prompt.txt
ENV PYTHONPATH=/app/src

EXPOSE 8001

CMD ["uvicorn", "argus.services.decision_agent.main:app", "--host", "0.0.0.0", "--port", "8001"]
