"""Internal pipeline schemas for the Knowledge & Context Agent."""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class RetrievalResult(BaseModel):
    """Result from a single knowledge retrieval tool."""
    source: str = Field(..., description="Name of the retrieval source (e.g. mitre, cve)")
    records: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved records")
    query_used: str = Field(default="", description="Query key used for lookup")
    hit_count: int = Field(default=0, description="Number of records found")

    class Config:
        arbitrary_types_allowed = True


class EnrichmentContext(BaseModel):
    """Aggregated retrieval results from all tools, ready for synthesis."""
    attack_type: str = Field(..., description="Normalized attack type from ThreatEvent")
    mitre_results: RetrievalResult = Field(default_factory=lambda: RetrievalResult(source="mitre_attack"))
    mitre_ics_results: RetrievalResult = Field(default_factory=lambda: RetrievalResult(source="mitre_attack_ics"))
    cve_results: RetrievalResult = Field(default_factory=lambda: RetrievalResult(source="cve_db"))
    cisa_results: RetrievalResult = Field(default_factory=lambda: RetrievalResult(source="cisa_advisories"))
    playbook_results: RetrievalResult = Field(default_factory=lambda: RetrievalResult(source="playbooks"))
    vector_results: RetrievalResult = Field(default_factory=lambda: RetrievalResult(source="vector_search"))

    class Config:
        arbitrary_types_allowed = True


class SynthesisResult(BaseModel):
    """Output of the GeminiReasoner after synthesizing all retrieval results."""
    attack_context: Dict[str, Any] = Field(..., description="Structured attack summary")
    mitre_techniques: List[Dict[str, Any]] = Field(default_factory=list)
    cves: List[Dict[str, Any]] = Field(default_factory=list)
    cisa_advisories: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_mitigations: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, description="Confidence of enrichment quality")
    summary_markdown: str = Field(default="", description="Human-readable markdown summary")


@dataclass
class KCAPipelineConfig:
    """Configuration for the Knowledge & Context Agent pipeline."""
    resources_dir: str = ""
    use_gemini: bool = False
    use_vector_search: bool = False
    confidence_threshold: float = 0.3
