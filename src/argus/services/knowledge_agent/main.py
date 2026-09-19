import os, json
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Constants & Configurations
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_CHROMA_DIR = str(PROJECT_ROOT / "knowledge_agent/chroma_db")

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", DEFAULT_CHROMA_DIR)
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "mitre_attack_ics")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

collection = None
chroma_client = None

class ContextQueryRequest(BaseModel):
    query: str = Field(..., description="Short text query or alert context describing the SCADA anomaly")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Number of top MITRE ATT&CK for ICS techniques to return (default: 3)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "SCADA Modbus command injection or unauthorized control message anomaly",
                "top_k": 3
            }
        }
    }

class TechniqueItem(BaseModel):
    technique_id: str = Field(..., description="MITRE ATT&CK technique ID (e.g. T0855)")
    name: str = Field(..., description="Technique name")
    description: str = Field(..., description="Technique detailed description")
    mitigations: List[str] = Field(..., description="Recommended MITRE mitigations")
    distance: float = Field(..., description="Vector embedding cosine/L2 distance score (lower is more relevant)")

class ContextResponse(BaseModel):
    query: str = Field(..., description="Original input query")
    techniques: List[TechniqueItem] = Field(..., description="Top-k matching MITRE ATT&CK for ICS techniques")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager loading ChromaDB collection once at application startup."""
    global collection, chroma_client
    chroma_path = Path(CHROMA_DB_DIR)
    if not chroma_path.exists():
        raise FileNotFoundError(f"Chroma DB directory not found at: {CHROMA_DB_DIR}. Please run ingest_attack.py first.")

    print(f"[*] Connecting to local Chroma persistent DB at: {CHROMA_DB_DIR}")
    chroma_client = chromadb.PersistentClient(path=str(chroma_path))
    
    print(f"[*] Loading embedding function: {EMBEDDING_MODEL}")
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

    print(f"[*] Accessing collection '{COLLECTION_NAME}'...")
    collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    print(f"[+] Knowledge collection loaded successfully with {collection.count()} techniques.")
    
    yield
    
    print("[*] Shutting down Knowledge Agent service.")

app = FastAPI(
    title="ARGUS Knowledge & Context Agent (MITRE ATT&CK for ICS)",
    description="FastAPI service querying local Chroma vector DB for top-3 relevant MITRE ATT&CK for ICS techniques.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    """Health check endpoint returning vector DB status and technique count."""
    count = collection.count() if collection is not None else 0
    return {
        "status": "healthy",
        "chroma_db_dir": CHROMA_DB_DIR,
        "collection_name": COLLECTION_NAME,
        "indexed_techniques_count": count,
        "embedding_model": EMBEDDING_MODEL
    }

@app.post("/context", response_model=ContextResponse)
def get_context(req: ContextQueryRequest):
    """
    POST /context endpoint.
    Accepts short text query and returns top-3 most relevant MITRE ATT&CK for ICS techniques.
    """
    if collection is None:
        raise HTTPException(status_code=503, detail="Vector collection is not initialized.")

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    top_k = req.top_k or 3

    # Query Chroma vector DB
    try:
        results = collection.query(
            query_texts=[req.query],
            n_results=top_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChromaDB query error: {str(e)}")

    if not results or "ids" not in results or not results["ids"]:
        return ContextResponse(query=req.query, techniques=[])

    techniques = []
    ids_list = results["ids"][0]
    metas_list = results["metadatas"][0]
    dists_list = results["distances"][0]

    for i in range(len(ids_list)):
        meta = metas_list[i]
        mitigations_json = meta.get("mitigations_json", "[]")
        try:
            mitigations = json.loads(mitigations_json)
        except Exception:
            mitigations = []

        techniques.append(TechniqueItem(
            technique_id=meta.get("technique_id", ids_list[i]),
            name=meta.get("name", "Unknown"),
            description=meta.get("description", ""),
            mitigations=mitigations,
            distance=round(float(dists_list[i]), 4)
        ))

    return ContextResponse(
        query=req.query,
        techniques=techniques
    )

from argus.services.common.base_agent import BaseAgent
from argus.services.common.schemas import AgentMessage

class KnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="KnowledgeAgent", role="Context Retrieval")

    async def process(self, message: AgentMessage) -> AgentMessage:
        payload = message.payload
        query_str = payload.get("query", "")
        
        if message.message_type == "review_request":
            # If reviewing, maybe fetch more results (e.g., top 5)
            top_k = payload.get("top_k", 5)
        else:
            top_k = payload.get("top_k", 3)

        try:
            results = collection.query(query_texts=[query_str], n_results=top_k)
            techniques = []
            if results and "ids" in results and results["ids"]:
                ids_list = results["ids"][0]
                metas_list = results["metadatas"][0]
                dists_list = results["distances"][0]

                for i in range(len(ids_list)):
                    meta = metas_list[i]
                    mit_json = meta.get("mitigations_json", "[]")
                    try:
                        mitigations = json.loads(mit_json)
                    except:
                        mitigations = []

                    techniques.append({
                        "technique_id": meta.get("technique_id", ids_list[i]),
                        "name": meta.get("name", "Unknown"),
                        "description": meta.get("description", ""),
                        "mitigations": mitigations,
                        "distance": round(float(dists_list[i]), 4)
                    })
        except Exception as e:
            techniques = [{"error": str(e)}]
        
        return AgentMessage(
            message_id=message.message_id + "-resp",
            event_id=message.event_id,
            sender=self.name,
            receiver=message.sender,
            message_type="response",
            payload={"query": query_str, "techniques": techniques},
            confidence=1.0,
            evidence={"context_length": len(techniques)},
            trace_id=message.trace_id
        )

knowledge_agent_instance = KnowledgeAgent()

@app.post("/agent/process", response_model=AgentMessage)
async def agent_process(message: AgentMessage):
    if collection is None:
        raise HTTPException(status_code=503, detail="Vector collection is not initialized.")
    try:
        return await knowledge_agent_instance.process(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
