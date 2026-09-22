"""Knowledge & Context Agent pipeline orchestrator."""
import time
from typing import Any, Dict

from argus.schemas.messages import KnowledgeEvent
from argus.agents.knowledge_context.schemas import (
    EnrichmentContext,
    KCAPipelineConfig,
)
from argus.agents.knowledge_context.tools import (
    MitreTool,
    MitreICSTool,
    CVETool,
    CISATool,
    PlaybookTool,
    VectorSearchTool,
    KnowledgePublisher,
)


class KnowledgePipeline:
    """Orchestrates the 9-stage knowledge enrichment pipeline.

    Stages
    ------
    1. Extract attack type from incoming ThreatEvent
    2. Retrieve MITRE ATT&CK Enterprise techniques
    3. Retrieve MITRE ATT&CK ICS techniques
    4. Retrieve CVE records
    5. Retrieve CISA ICS-CERT advisories
    6. Retrieve internal playbooks
    7. Vector search (future — currently no-op)
    8. Gemini synthesis / summarization
    9. Build and return KnowledgeEvent
    """

    def __init__(self, agent_id: str, config: KCAPipelineConfig):
        self.agent_id = agent_id
        self.config = config

        rd = config.resources_dir
        self.mitre = MitreTool(resources_dir=rd)
        self.mitre_ics = MitreICSTool(resources_dir=rd)
        self.cve = CVETool(resources_dir=rd)
        self.cisa = CISATool(resources_dir=rd)
        self.playbook = PlaybookTool(resources_dir=rd)
        self.vector = VectorSearchTool(resources_dir=rd)
        self.publisher = KnowledgePublisher(resources_dir=rd)

    async def initialize(self) -> None:
        """Initialize all pipeline tools (load JSON databases)."""
        await self.mitre.initialize()
        await self.mitre_ics.initialize()
        await self.cve.initialize()
        await self.cisa.initialize()
        await self.playbook.initialize()
        await self.vector.initialize()
        await self.publisher.initialize()

    async def shutdown(self) -> None:
        """Shutdown all pipeline tools."""
        await self.mitre.shutdown()
        await self.mitre_ics.shutdown()
        await self.cve.shutdown()
        await self.cisa.shutdown()
        await self.playbook.shutdown()
        await self.vector.shutdown()
        await self.publisher.shutdown()

    def _normalize_attack_type(self, raw: str) -> str:
        """Normalize attack type string for consistent lookup."""
        return raw.strip().lower().replace(" ", "_").replace("-", "_")

    async def process_threat(self, threat_data: Dict[str, Any]) -> KnowledgeEvent:
        """Run the full enrichment pipeline on a single ThreatEvent payload.

        Parameters
        ----------
        threat_data : dict
            A dictionary containing at least ``attack_type``. May also
            contain ``cve_id`` and ``mitre_technique_id`` for direct lookups.

        Returns
        -------
        KnowledgeEvent
            Enriched knowledge event ready for publication.
        """
        start_time = time.time()

        # Stage 1: Extract attack type
        attack_type = self._normalize_attack_type(threat_data.get("attack_type", "unknown"))
        cve_id = threat_data.get("cve_id")

        # Stages 2–6: Parallel retrieval (executed sequentially for simplicity;
        # could be wrapped in asyncio.gather for production throughput)
        mitre_result = await self.mitre.execute(attack_type=attack_type)
        mitre_ics_result = await self.mitre_ics.execute(attack_type=attack_type)
        cve_result = await self.cve.execute(attack_type=attack_type, cve_id=cve_id)
        cisa_result = await self.cisa.execute(attack_type=attack_type)
        playbook_result = await self.playbook.execute(attack_type=attack_type)

        # Stage 7: Vector search (future)
        vector_result = await self.vector.execute(query=attack_type)

        # Assemble enrichment context
        enrichment = EnrichmentContext(
            attack_type=attack_type,
            mitre_results=mitre_result,
            mitre_ics_results=mitre_ics_result,
            cve_results=cve_result,
            cisa_results=cisa_result,
            playbook_results=playbook_result,
            vector_results=vector_result,
        )

        # Stage 8: Synthesis

        # Stage 9: Build KnowledgeEvent
        duration_ms = (time.time() - start_time) * 1000.0
        event = await self.publisher.execute(
            synthesis_result="None",
            agent_id=self.agent_id,
            processing_duration_ms=duration_ms,
        )

        return event
