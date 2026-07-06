"""MitreICSTool — Retrieves MITRE ATT&CK ICS techniques from local JSON database."""
import json
import os
from typing import Any, Dict, List

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.knowledge_context.schemas import RetrievalResult


class MitreICSTool(BaseTool):
    """Retrieves MITRE ATT&CK for ICS techniques relevant to a given attack type."""

    def __init__(self, resources_dir: str = ""):
        super().__init__(
            tool_id="tool-mitre-ics-kca-01",
            name="mitre_attack_ics",
            version="1.0.0",
            category=ToolCategory.SECURITY,
            description="MITRE ATT&CK ICS technique lookup for industrial control systems.",
            required_permissions=["read:security_context"],
        )
        self._resources_dir = resources_dir
        self._db: Dict[str, Any] = {}

    async def initialize(self) -> None:
        path = os.path.join(self._resources_dir, "mitre_attack_ics.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self._db = json.load(f)
            self.logger.info("mitre_ics_db_loaded", record_count=len(self._db.get("techniques", {})))
        else:
            self.logger.warning("mitre_ics_db_not_found", path=path)

    async def validate(self, **kwargs: Any) -> bool:
        return "attack_type" in kwargs

    def _lookup(self, attack_type: str) -> List[Dict[str, Any]]:
        mapping = self._db.get("attack_type_mapping", {})
        technique_ids = mapping.get(attack_type, mapping.get("default", []))
        techniques = self._db.get("techniques", {})
        return [techniques[tid] for tid in technique_ids if tid in techniques]

    async def execute(self, **kwargs: Any) -> RetrievalResult:
        attack_type: str = kwargs["attack_type"]
        records = self._lookup(attack_type)
        return RetrievalResult(
            source="mitre_attack_ics",
            records=records,
            query_used=attack_type,
            hit_count=len(records),
        )

    async def shutdown(self) -> None:
        self._db = {}

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {"attack_type": {"type": "string"}},
            "required": ["attack_type"],
        }
        return md
