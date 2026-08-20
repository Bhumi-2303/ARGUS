# ARGUS Knowledge & Context Agent (MITRE ATT&CK for ICS)

FastAPI microservice vector store for the **ARGUS project** providing semantic retrieval of **MITRE ATT&CK for ICS** techniques and mitigations using local embeddings and Chroma vector database.

---

## 🚀 Features

- **Local Vector Store**: Persistent Chroma vector database (`chroma_db/`) indexing 97 active MITRE ATT&CK for ICS techniques.
- **Local Embedding Model**: Uses `sentence-transformers` (`all-MiniLM-L6-v2`) — **100% local execution with zero cloud calls**.
- **Official STIX Dataset**: Ingests public STIX 2.1 data from MITRE's official `attack-stix-data` repository (`ics-attack` collection).
- **Re-runnable Ingestion Script**: `ingest_attack.py` generates an explicit JSON reproducibility report (`ingestion_reproducibility_report.json`) for research paper methodology sections.

---

## 📌 Endpoints

### 1. `GET /health`
Returns service status, vector store path, technique count, and embedding model name.

**Example Response**:
```json
{
  "status": "healthy",
  "chroma_db_dir": "/Users/tirthkosambia/Documents/ARGUS/knowledge_agent/chroma_db",
  "collection_name": "mitre_attack_ics",
  "indexed_techniques_count": 97,
  "embedding_model": "all-MiniLM-L6-v2"
}
```

### 2. `POST /context`
Accepts a short text query (e.g., describing a SCADA anomaly or protocol flag mismatch) and returns the top 3 most relevant MITRE ATT&CK for ICS techniques.

**Example Request**:
```bash
curl -X POST "http://localhost:8003/context" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "SCADA Modbus command injection or length anomaly",
       "top_k": 3
     }'
```

**Example Response**:
```json
{
  "query": "SCADA Modbus command injection or length anomaly",
  "techniques": [
    {
      "technique_id": "T0843.003",
      "name": "Program Append",
      "description": "Adversaries may execute a program append to a PLC to update parts of an existing program...",
      "mitigations": [
        "M0937: Filter Network Traffic",
        "M0930: Network Segmentation",
        "M0801: Access Management"
      ],
      "distance": 0.6116
    },
    {
      "technique_id": "T0843.002",
      "name": "Online Edit",
      "description": "Adversaries may execute an online edit of a PLC...",
      "mitigations": ["M0937: Filter Network Traffic"],
      "distance": 0.6431
    },
    {
      "technique_id": "T0827",
      "name": "Loss of Control",
      "description": "Adversaries may seek to achieve a sustained loss of control...",
      "mitigations": ["M0953: Data Backup"],
      "distance": 0.6482
    }
  ]
}
```

---

## 🏃 Ingestion & Local Running

```bash
# 1. Re-run ingestion script (downloads STIX, embeds, & indexes ChromaDB)
PYTHONPATH=. .venv/bin/python knowledge_agent/ingest_attack.py

# 2. Start Knowledge Agent service on Port 8003
PYTHONPATH=. uvicorn knowledge_agent.main:app --host 0.0.0.0 --port 8003

# 3. Run Unit Test Suite
PYTHONPATH=. .venv/bin/python knowledge_agent/test_knowledge_agent.py
```

---

## 🐳 Docker Support

```bash
# Build Docker image
docker build -t argus-knowledge-agent -f knowledge_agent/Dockerfile .

# Run Container
docker run -d -p 8003:8003 --name argus-knowledge-agent argus-knowledge-agent
```
