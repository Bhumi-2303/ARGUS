"""Vector memory for semantic search."""
from typing import Any, Dict, List, Optional
import structlog
from config.settings import get_settings

logger = structlog.get_logger("argus.memory.vector")

class VectorMemory:
    """Wrapper for ChromaDB vector store."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.settings = get_settings()
        self._client = None
        self._collection = None
        
    async def _init_client(self) -> None:
        """Lazy initialization of ChromaDB."""
        if not self.settings.features.vector_memory:
            return
            
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=self.settings.db.chromadb_path)
                self._collection = self._client.get_or_create_collection(name=self.collection_name)
            except Exception as e:
                logger.error("chromadb_init_failed", error=str(e))
                self._client = False # Mark as failed
                
    async def store(self, doc_id: str, text: str, metadata: Dict[str, Any], embedding: Optional[List[float]] = None) -> bool:
        """Store a document in vector memory."""
        await self._init_client()
        if not self._collection:
            return False
            
        try:
            kwargs = {
                "ids": [doc_id],
                "documents": [text],
                "metadatas": [metadata]
            }
            if embedding:
                kwargs["embeddings"] = [embedding]
                
            self._collection.upsert(**kwargs)
            return True
        except Exception as e:
            logger.error("vector_store_failed", error=str(e), doc_id=doc_id)
            return False
            
    async def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search vector memory for similar documents."""
        await self._init_client()
        if not self._collection:
            return []
            
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results and results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results and results["distances"] else None
                    })
            return formatted_results
        except Exception as e:
            logger.error("vector_search_failed", error=str(e))
            return []
