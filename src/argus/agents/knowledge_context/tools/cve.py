"""CVETool — Retrieves CVE vulnerability data from local JSON database."""
import json
import os
from typing import Any, Dict, List

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.knowledge_context.schemas import RetrievalResult


class CVETool(BaseTool):
    """Retrieves CVE records relevant to a given attack type or specific CVE ID."""

    def __init__(self, resources_dir: str = ""):
        super().__init__(
            tool_id="tool-cve-kca-01",
            name="cve_lookup",
            version="1.0.0",
            category=ToolCategory.SECURITY,
            description="CVE vulnerability database lookup.",
            required_permissions=["read:security_context"],
        )
        self._resources_dir = resources_dir
        self._db: Dict[str, Any] = {}

    async def initialize(self) -> None:
        path = os.path.join(self._resources_dir, "cve_db.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self._db = json.load(f)
            self.logger.info("cve_db_loaded", record_count=len(self._db.get("cves", {})))
        else:
            self.logger.warning("cve_db_not_found", path=path)

    async def validate(self, **kwargs: Any) -> bool:
        return "attack_type" in kwargs or "cve_id" in kwargs

    def _lookup_by_attack_type(self, attack_type: str) -> List[Dict[str, Any]]:
        mapping = self._db.get("attack_type_mapping", {})
        cve_ids = mapping.get(attack_type, mapping.get("default", []) if attack_type not in ("benign", "normal", "unknown") else [])
        cves = self._db.get("cves", {})
        return [cves[cid] for cid in cve_ids if cid in cves]

    def _lookup_by_id(self, cve_id: str) -> List[Dict[str, Any]]:
        cves = self._db.get("cves", {})
        if cve_id in cves:
            return [cves[cve_id]]
        return []

    async def execute(self, **kwargs: Any) -> RetrievalResult:
        cve_id = kwargs.get("cve_id")
        attack_type = kwargs.get("attack_type", "")

        if cve_id:
            records = self._lookup_by_id(cve_id)
            query = cve_id
        else:
            records = self._lookup_by_attack_type(attack_type)
            query = attack_type

        return RetrievalResult(
            source="cve_db",
            records=records,
            query_used=query,
            hit_count=len(records),
        )

    async def shutdown(self) -> None:
        self._db = {}

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {
                "attack_type": {"type": "string"},
                "cve_id": {"type": "string"},
            },
        }
        return md
