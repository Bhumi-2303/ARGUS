"""Read-only Model Context Protocol (MCP) server for ARGUS.

Exposes inspection tools and resources over existing ARGUS services.
SAFETY GUARANTEE:
- All tools are strictly read-only.
- Never mutates pipeline state, database records, risk scores, or decisions.
- Completely isolated from the detection path.
"""

import json
import os
from typing import Any, Dict, List, Optional
import structlog

from argus.tools.mcp.base_mcp_server import BaseMCPServer
from argus.registry.model_registry import model_registry, MODEL_METADATA

logger = structlog.get_logger("argus.integrations.mcp")


class ArgusMCPServer(BaseMCPServer):
    """Production read-only MCP server exposing ARGUS inspection tools.
    
    Tools:
    - get_incident: Inspect incident details, timeline, risk score, and actions.
    - get_trace: Inspect pipeline execution trace and stage latencies.
    - explain_flow: Compute TreeSHAP feature attributions for a given flow.
    - lookup_mitre: Lookup MITRE ATT&CK techniques, descriptions, and mitigations.
    """

    def __init__(self, name: str = "argus-mcp", version: str = "1.0.0", resources_dir: Optional[str] = None):
        super().__init__(name=name, version=version)
        self.logger = logger.bind(server=self.name, version=self.version)
        self._initialized = False
        self._mitre_db: Dict[str, Any] = {}
        
        # Locate knowledge context resources
        if resources_dir:
            self._resources_dir = resources_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self._resources_dir = os.path.join(base_dir, "agents", "knowledge_context", "resources")

    async def initialize(self) -> None:
        """Initialize connection to internal read-only data sources."""
        if self._initialized:
            return

        # Load MITRE ATT&CK local JSON database for fast offline lookup
        mitre_path = os.path.join(self._resources_dir, "mitre_attack.json")
        if os.path.exists(mitre_path):
            try:
                with open(mitre_path, "r", encoding="utf-8") as f:
                    self._mitre_db = json.load(f)
                self.logger.info("mcp_mitre_db_loaded", techniques_count=len(self._mitre_db.get("techniques", {})))
            except Exception as e:
                self.logger.warning("mcp_mitre_db_load_error", error=str(e))
        else:
            self.logger.warning("mcp_mitre_db_missing", path=mitre_path)

        # Ensure model registry is loaded for read-only SHAP explanations
        if not model_registry.is_loaded:
            try:
                model_registry.load_all()
            except Exception as e:
                self.logger.warning("mcp_model_registry_init_warning", error=str(e))

        self._initialized = True
        self.logger.info("argus_mcp_server_initialized")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List the 4 read-only tools provided by this server."""
        return [
            {
                "name": "get_incident",
                "description": "Retrieve security incident details, status, risk score, and recommended actions by incident ID.",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "incident_id": {
                            "type": "string",
                            "description": "Unique identifier of the incident (e.g., 'INC-20261104-001' or UUID)."
                        }
                    },
                    "required": ["incident_id"]
                },
                "read_only": True
            },
            {
                "name": "get_trace",
                "description": "Retrieve multi-agent execution steps, latencies, and stage summaries for a correlation ID.",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "correlation_id": {
                            "type": "string",
                            "description": "Correlation ID of the pipeline execution flow (e.g., 'flow-3c3d627c')."
                        }
                    },
                    "required": ["correlation_id"]
                },
                "read_only": True
            },
            {
                "name": "explain_flow",
                "description": "Compute TreeSHAP feature attributions and attack probability for flow features using verified models.",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "features": {
                            "type": "object",
                            "description": "Dictionary of feature values (e.g. pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max)."
                        },
                        "model_name": {
                            "type": "string",
                            "description": "Model identifier to explain against. Defaults to 'model_d2_coral'.",
                            "default": "model_d2_coral"
                        }
                    },
                    "required": ["features"]
                },
                "read_only": True
            },
            {
                "name": "lookup_mitre",
                "description": "Lookup MITRE ATT&CK techniques, descriptions, tactics, and mitigations by technique ID or attack type.",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "technique_id": {
                            "type": "string",
                            "description": "MITRE technique ID (e.g., 'T1059', 'T1110', 'T0814')."
                        },
                        "attack_type": {
                            "type": "string",
                            "description": "General attack classification (e.g., 'brute_force', 'ddos', 'reconnaissance', 'c2')."
                        }
                    }
                },
                "read_only": True
            }
        ]

    async def call_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a read-only tool call with strict boundary validation."""
        if not self._initialized:
            await self.initialize()

        args = args or {}

        if name == "get_incident":
            return await self._tool_get_incident(args.get("incident_id"))
        elif name == "get_trace":
            return await self._tool_get_trace(args.get("correlation_id"))
        elif name == "explain_flow":
            return await self._tool_explain_flow(
                features=args.get("features", {}),
                model_name=args.get("model_name", "model_d2_coral")
            )
        elif name == "lookup_mitre":
            return await self._tool_lookup_mitre(
                technique_id=args.get("technique_id"),
                attack_type=args.get("attack_type")
            )
        else:
            raise ValueError(f"Unknown tool '{name}'. Available: get_incident, get_trace, explain_flow, lookup_mitre")

    async def _tool_get_incident(self, incident_id: Optional[str]) -> Dict[str, Any]:
        """Read-only tool: Retrieve incident by ID."""
        if not incident_id:
            return {"found": False, "error": "Missing required parameter 'incident_id'"}

        from argus.services.incident_service import incident_service
        incident = incident_service.get_incident(incident_id)

        if incident is None:
            return {
                "found": False,
                "incident_id": incident_id,
                "error": f"Incident '{incident_id}' not found in active cache or durable store."
            }

        # Safely convert to read-only dict
        data = incident.model_dump() if hasattr(incident, "model_dump") else dict(incident)

        # Extract actions either directly or from decision payload
        actions = data.get("recommended_actions")
        if actions is None and isinstance(data.get("decision"), dict):
            actions = data.get("decision", {}).get("recommendations", [])
        actions = actions or []

        # Extract MITRE techniques either directly or from knowledge_summary
        mitre = data.get("mitre_techniques")
        if mitre is None and data.get("knowledge_summary"):
            mitre = [t.strip() for t in str(data["knowledge_summary"]).split(",") if t.strip()]
        mitre = mitre or []

        return {
            "found": True,
            "incident_id": data.get("incident_id"),
            "event_id": data.get("event_id"),
            "status": str(data.get("status")),
            "severity": str(data.get("severity")),
            "asset": data.get("asset"),
            "threat_level": data.get("threat_level") or data.get("detector_summary", "UNKNOWN"),
            "risk_score": data.get("risk_score"),
            "confidence": data.get("confidence"),
            "source_ip": data.get("source_ip"),
            "destination_ip": data.get("destination_ip"),
            "mitre_techniques": mitre,
            "recommended_actions": actions,
            "created_at": str(data.get("created_at")),
            "updated_at": str(data.get("updated_at")),
            "timeline": data.get("timeline", []),
        }

    async def _tool_get_trace(self, correlation_id: Optional[str]) -> Dict[str, Any]:
        """Read-only tool: Retrieve multi-agent execution trace by correlation ID."""
        if not correlation_id:
            return {"found": False, "error": "Missing required parameter 'correlation_id'"}

        from argus.orchestrator.store import IncidentStore
        store = IncidentStore()
        run_data = store.get_pipeline_run(correlation_id)

        if run_data is None:
            return {
                "found": False,
                "correlation_id": correlation_id,
                "error": f"Pipeline trace for correlation_id '{correlation_id}' not found in durable store."
            }

        return {
            "found": True,
            "correlation_id": run_data.get("correlation_id"),
            "event_id": run_data.get("event_id"),
            "status": run_data.get("status"),
            "model_name": run_data.get("model_name"),
            "started_at": run_data.get("started_at"),
            "completed_at": run_data.get("completed_at"),
            "incident_id": run_data.get("incident_id"),
            "approval_status": run_data.get("approval_status"),
            "traces": run_data.get("traces", []),
            "total_stages": len(run_data.get("traces", [])),
        }

    async def _tool_explain_flow(self, features: Dict[str, Any], model_name: str = "model_d2_coral") -> Dict[str, Any]:
        """Read-only tool: Compute TreeSHAP attributions for given features."""
        if not features or not isinstance(features, dict):
            return {"success": False, "error": "Parameter 'features' must be a non-empty dictionary of float values."}

        # Convert feature values to floats
        clean_features = {}
        for k, v in features.items():
            try:
                clean_features[k] = float(v)
            except (ValueError, TypeError):
                continue

        if not clean_features:
            return {"success": False, "error": "No valid numerical features provided."}

        try:
            base_val, shap_dict, top_feat, top_impact = model_registry.explain(model_name, clean_features)
            prob, _label, _thresh = model_registry.predict(model_name, clean_features)

            return {
                "success": True,
                "model_name": model_name,
                "probability": float(prob),
                "is_anomalous": bool(prob >= 0.50),
                "base_value": float(base_val),
                "top_feature": top_feat,
                "top_feature_impact": float(top_impact),
                "shap_attributions": shap_dict,
            }
        except Exception as e:
            return {
                "success": False,
                "model_name": model_name,
                "error": f"SHAP explanation failed: {str(e)}"
            }

    async def _tool_lookup_mitre(
        self,
        technique_id: Optional[str] = None,
        attack_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Read-only tool: Lookup MITRE ATT&CK techniques."""
        techniques = self._mitre_db.get("techniques", {})
        mapping = self._mitre_db.get("attack_type_mapping", {})

        # Direct technique lookup
        if technique_id:
            tid = technique_id.strip().upper()
            if tid in techniques:
                return {
                    "found": True,
                    "query_type": "technique_id",
                    "technique_id": tid,
                    "technique": techniques[tid],
                }
            return {
                "found": False,
                "query_type": "technique_id",
                "technique_id": tid,
                "error": f"MITRE technique '{tid}' not found in local database.",
                "available_ids": sorted(list(techniques.keys()))[:10]
            }

        # Attack type category lookup
        if attack_type:
            atype = attack_type.strip().lower()
            matched_ids = mapping.get(atype, [])
            if not matched_ids and atype not in ("benign", "normal"):
                # Fallback fuzzy match
                for map_key, map_ids in mapping.items():
                    if atype in map_key or map_key in atype:
                        matched_ids = map_ids
                        break

            matched_techniques = [techniques[tid] for tid in matched_ids if tid in techniques]
            return {
                "found": len(matched_techniques) > 0,
                "query_type": "attack_type",
                "attack_type": atype,
                "matched_count": len(matched_techniques),
                "techniques": matched_techniques,
            }

        # If neither specified, return general index
        return {
            "found": True,
            "query_type": "summary",
            "total_techniques": len(techniques),
            "available_technique_ids": sorted(list(techniques.keys())),
            "available_attack_types": sorted(list(mapping.keys())),
        }

    async def list_resources(self) -> List[Dict[str, Any]]:
        """List read-only resources available on this server."""
        return [
            {
                "uri": "argus://incidents",
                "name": "Active Security Incidents",
                "description": "List of recent security incidents and risk assessments.",
                "mimeType": "application/json"
            },
            {
                "uri": "argus://models",
                "name": "Verified Model Registry",
                "description": "List of loaded detection models, weights status, and expected feature counts.",
                "mimeType": "application/json"
            },
            {
                "uri": "argus://mitre",
                "name": "MITRE ATT&CK Catalog",
                "description": "Index of supported MITRE ATT&CK Enterprise techniques.",
                "mimeType": "application/json"
            }
        ]

    async def read_resource(self, uri: str) -> Any:
        """Read a specified read-only resource."""
        if not self._initialized:
            await self.initialize()

        if uri == "argus://incidents":
            from argus.services.incident_service import incident_service
            incidents = incident_service.list_incidents(limit=20)
            return [
                {
                    "incident_id": inc.incident_id,
                    "status": inc.status,
                    "severity": inc.severity,
                    "risk_score": inc.risk_score,
                    "threat_level": inc.threat_level,
                    "created_at": str(inc.created_at)
                }
                for inc in incidents
            ]
        elif uri == "argus://models":
            return [
                {
                    "model_name": name,
                    "is_loaded": name in model_registry.loaded_models,
                    "feature_count": meta.get("features", 4),
                    "description": meta.get("description", ""),
                    "status": meta.get("status", "unknown"),
                }
                for name, meta in MODEL_METADATA.items()
            ]
        elif uri == "argus://mitre":
            techniques = self._mitre_db.get("techniques", {})
            return [
                {"id": tid, "name": tech.get("name"), "tactic": tech.get("tactic")}
                for tid, tech in techniques.items()
            ]
        else:
            raise KeyError(f"Resource with URI '{uri}' not found.")

    async def shutdown(self) -> None:
        """Cleanly shutdown the MCP server."""
        self._mitre_db.clear()
        self._initialized = False
        self.logger.info("argus_mcp_server_shutdown")
