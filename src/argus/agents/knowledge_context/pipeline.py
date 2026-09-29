"""Knowledge & Context Agent pipeline orchestrator."""
import time
from typing import Any, Dict

from argus.schemas.messages import KnowledgeEvent
from argus.agents.knowledge_context.schemas import (
    EnrichmentContext,
    KCAPipelineConfig,
    SynthesisResult,
)
from argus.agents.knowledge_context.tools import (
    MitreTool,
    MitreICSTool,
    CVETool,
    CISATool,
    PlaybookTool,
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
        self.publisher = KnowledgePublisher(resources_dir=rd)

    async def initialize(self) -> None:
        """Initialize all pipeline tools (load JSON databases)."""
        await self.mitre.initialize()
        await self.mitre_ics.initialize()
        await self.cve.initialize()
        await self.cisa.initialize()
        await self.playbook.initialize()
        await self.publisher.initialize()

    async def shutdown(self) -> None:
        """Shutdown all pipeline tools."""
        await self.mitre.shutdown()
        await self.mitre_ics.shutdown()
        await self.cve.shutdown()
        await self.cisa.shutdown()
        await self.playbook.shutdown()
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

        # Stage 8: Synthesis — Build SynthesisResult from actual enrichment data
        sources_consulted = []
        total_records = 0
        for src_name, result in [
            ("mitre_attack", mitre_result),
            ("mitre_ics", mitre_ics_result),
            ("cve", cve_result),
            ("cisa", cisa_result),
            ("playbook", playbook_result),
        ]:
            sources_consulted.append(src_name)
            total_records += result.hit_count

        # Extract recommended mitigations from playbook results
        recommended_mitigations = []
        for rec in playbook_result.records:
            if isinstance(rec, dict) and "recommendation" in rec:
                recommended_mitigations.append(rec["recommendation"])
            elif isinstance(rec, dict) and "description" in rec:
                recommended_mitigations.append(rec["description"])

        # Calculate confidence based on how many sources returned results
        sources_with_hits = sum(
            1 for r in [mitre_result, mitre_ics_result, cve_result, cisa_result, playbook_result]
            if r.hit_count > 0
        )
        confidence = min(1.0, sources_with_hits * 0.2)

        synthesis = SynthesisResult(
            attack_context={
                "attack_type": attack_type,
                "sources_consulted": sources_consulted,
                "total_records_retrieved": total_records,
            },
            mitre_techniques=mitre_result.records + mitre_ics_result.records,
            cves=cve_result.records,
            cisa_advisories=cisa_result.records,
            recommended_mitigations=recommended_mitigations,
            references=[],
            confidence=confidence,
            summary_markdown="",
        )

        # Stage 9: Build KnowledgeEvent
        duration_ms = (time.time() - start_time) * 1000.0
        event = await self.publisher.execute(
            synthesis_result=synthesis,
            agent_id=self.agent_id,
            processing_duration_ms=duration_ms,
            event_id=threat_data.get("event_id"),
            correlation_id=threat_data.get("correlation_id"),
        )

        return event
