"""GeminiReasoner — Synthesizes retrieval results into a structured knowledge summary."""
from typing import Any, Dict, List

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.knowledge_context.schemas import EnrichmentContext, SynthesisResult


class GeminiReasoner(BaseTool):
    """Synthesizes all retrieval results into a coherent knowledge summary.

    Currently uses deterministic template-based synthesis. When a live
    Gemini API connection is available, the ``_synthesize`` method will
    call the LLM for richer contextual reasoning.
    """

    def __init__(self, resources_dir: str = ""):
        super().__init__(
            tool_id="tool-gemini-kca-01",
            name="gemini_reasoner",
            version="1.0.0",
            category=ToolCategory.LLM,
            description="Synthesizes threat intelligence into structured knowledge context.",
            required_permissions=["execute:llm"],
        )
        self._use_live_gemini = False

    async def initialize(self) -> None:
        self.logger.info("gemini_reasoner_initialized", mode="template")

    async def validate(self, **kwargs: Any) -> bool:
        return "enrichment_context" in kwargs

    def _collect_mitigations(self, ctx: EnrichmentContext) -> List[str]:
        """Collect and de-duplicate mitigations across all sources."""
        mitigations: List[str] = []
        seen: set = set()

        for record in ctx.mitre_results.records:
            for m in record.get("mitigations", []):
                if m not in seen:
                    mitigations.append(m)
                    seen.add(m)

        for record in ctx.mitre_ics_results.records:
            for m in record.get("mitigations", []):
                if m not in seen:
                    mitigations.append(m)
                    seen.add(m)

        for record in ctx.cve_results.records:
            patch = record.get("patch", "")
            if patch and patch not in seen:
                mitigations.append(f"Patch: {patch}")
                seen.add(patch)

        for record in ctx.cisa_results.records:
            for r in record.get("recommendations", []):
                if r not in seen:
                    mitigations.append(r)
                    seen.add(r)

        for record in ctx.playbook_results.records:
            for action in record.get("immediate_actions", []):
                if action not in seen:
                    mitigations.append(action)
                    seen.add(action)
            for action in record.get("recovery_actions", []):
                if action not in seen:
                    mitigations.append(action)
                    seen.add(action)

        return mitigations

    def _collect_references(self, ctx: EnrichmentContext) -> List[str]:
        """Collect and de-duplicate external references."""
        refs: List[str] = []
        seen: set = set()
        for source in [ctx.mitre_results, ctx.mitre_ics_results, ctx.cve_results, ctx.cisa_results]:
            for record in source.records:
                for ref in record.get("references", []):
                    if ref not in seen:
                        refs.append(ref)
                        seen.add(ref)
        return refs

    def _compute_confidence(self, ctx: EnrichmentContext) -> float:
        """Compute a simple confidence score based on retrieval coverage."""
        total_sources = 5  # mitre, mitre_ics, cve, cisa, playbook
        hits = sum([
            1 if ctx.mitre_results.hit_count > 0 else 0,
            1 if ctx.mitre_ics_results.hit_count > 0 else 0,
            1 if ctx.cve_results.hit_count > 0 else 0,
            1 if ctx.cisa_results.hit_count > 0 else 0,
            1 if ctx.playbook_results.hit_count > 0 else 0,
        ])
        return round(hits / total_sources, 2)

    def _build_attack_context(self, ctx: EnrichmentContext) -> Dict[str, Any]:
        """Build the structured attack context dictionary."""
        context: Dict[str, Any] = {
            "attack_type": ctx.attack_type,
            "sources_consulted": [],
            "total_records_retrieved": 0,
        }

        for source_result in [ctx.mitre_results, ctx.mitre_ics_results, ctx.cve_results,
                               ctx.cisa_results, ctx.playbook_results]:
            if source_result.hit_count > 0:
                context["sources_consulted"].append(source_result.source)
                context["total_records_retrieved"] += source_result.hit_count

        # Add top-level summary from first MITRE technique if available
        if ctx.mitre_results.records:
            first = ctx.mitre_results.records[0]
            context["primary_technique"] = first.get("name", "Unknown")
            context["primary_tactic"] = first.get("tactic", "Unknown")
            context["technique_description"] = first.get("description", "")

        return context

    def _build_summary_markdown(self, ctx: EnrichmentContext, mitigations: List[str]) -> str:
        """Generate a human-readable markdown summary."""
        lines = [f"# Threat Intelligence Summary: {ctx.attack_type.replace('_', ' ').title()}\n"]

        if ctx.mitre_results.records:
            lines.append("## MITRE ATT&CK Enterprise Techniques\n")
            for t in ctx.mitre_results.records:
                lines.append(f"- **{t['id']}** — {t['name']} ({t.get('tactic', 'N/A')})")
            lines.append("")

        if ctx.mitre_ics_results.records:
            lines.append("## MITRE ATT&CK ICS Techniques\n")
            for t in ctx.mitre_ics_results.records:
                lines.append(f"- **{t['id']}** — {t['name']} ({t.get('tactic', 'N/A')})")
            lines.append("")

        if ctx.cve_results.records:
            lines.append("## Related CVEs\n")
            for c in ctx.cve_results.records:
                lines.append(f"- **{c['id']}** (CVSS {c.get('cvss_score', 'N/A')}) — {c.get('description', '')[:120]}...")
            lines.append("")

        if ctx.cisa_results.records:
            lines.append("## CISA ICS-CERT Advisories\n")
            for a in ctx.cisa_results.records:
                lines.append(f"- **{a['id']}** — {a.get('title', 'N/A')}")
            lines.append("")

        if mitigations:
            lines.append("## Recommended Mitigations\n")
            for i, m in enumerate(mitigations[:15], 1):
                lines.append(f"{i}. {m}")
            lines.append("")

        return "\n".join(lines)

    async def execute(self, **kwargs: Any) -> SynthesisResult:
        ctx: EnrichmentContext = kwargs["enrichment_context"]

        mitigations = self._collect_mitigations(ctx)
        references = self._collect_references(ctx)
        confidence = self._compute_confidence(ctx)
        attack_context = self._build_attack_context(ctx)
        summary = self._build_summary_markdown(ctx, mitigations)

        return SynthesisResult(
            attack_context=attack_context,
            mitre_techniques=ctx.mitre_results.records + ctx.mitre_ics_results.records,
            cves=ctx.cve_results.records,
            cisa_advisories=ctx.cisa_results.records,
            recommended_mitigations=mitigations,
            references=references,
            confidence=confidence,
            summary_markdown=summary,
        )

    async def shutdown(self) -> None:
        pass

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {"enrichment_context": {"type": "object"}},
            "required": ["enrichment_context"],
        }
        return md
