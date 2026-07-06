"""CISATool — Retrieves CISA ICS-CERT advisories from local JSON database."""
import json
import os
from typing import Any, Dict, List

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.knowledge_context.schemas import RetrievalResult


class CISATool(BaseTool):
    """Retrieves CISA ICS-CERT advisories relevant to a given attack type."""

    def __init__(self, resources_dir: str = ""):
        super().__init__(
            tool_id="tool-cisa-kca-01",
            name="cisa_advisories",
            version="1.0.0",
            category=ToolCategory.SECURITY,
            description="CISA ICS-CERT advisory lookup.",
            required_permissions=["read:security_context"],
        )
        self._resources_dir = resources_dir
        self._db: Dict[str, Any] = {}

    async def initialize(self) -> None:
        path = os.path.join(self._resources_dir, "cisa_advisories.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self._db = json.load(f)
            self.logger.info("cisa_db_loaded", record_count=len(self._db.get("advisories", {})))
        else:
            self.logger.warning("cisa_db_not_found", path=path)

    async def validate(self, **kwargs: Any) -> bool:
        return "attack_type" in kwargs

    def _lookup(self, attack_type: str) -> List[Dict[str, Any]]:
        mapping = self._db.get("attack_type_mapping", {})
        advisory_ids = mapping.get(attack_type, mapping.get("default", []))
        advisories = self._db.get("advisories", {})
        return [advisories[aid] for aid in advisory_ids if aid in advisories]

    async def execute(self, **kwargs: Any) -> RetrievalResult:
        attack_type: str = kwargs["attack_type"]
        records = self._lookup(attack_type)
        return RetrievalResult(
            source="cisa_advisories",
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
