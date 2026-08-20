FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code and system prompt file
COPY agent/main.py /app/agent/main.py
COPY prompts/decision_support_system_prompt.txt /app/prompts/decision_support_system_prompt.txt

# Environment variables
ENV DETECTOR_API_URL=http://detector-api:8000/predict
ENV OLLAMA_API_URL=http://ollama:11434
ENV OLLAMA_MODEL=llama3.2
ENV PROMPT_PATH=/app/prompts/decision_support_system_prompt.txt
ENV PYTHONPATH=/app

EXPOSE 8001

# Start Uvicorn server
CMD ["uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8001"]
