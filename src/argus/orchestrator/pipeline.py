"""Real end-to-end agent execution pipeline for ARGUS."""
import asyncio
import inspect
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import structlog

from argus.registry.model_registry import model_registry

logger = structlog.get_logger("argus.pipeline")

@dataclass
class TraceEvent:
    agent: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    error: Optional[str] = None
    model_version: Optional[str] = None

    @property
    def stage(self) -> str:
        return self.agent

    @property
    def duration_ms(self) -> Optional[float]:
        return self.duration

    @property
    def start_time(self) -> Optional[datetime]:
        return self.started_at

    @property
    def end_time(self) -> Optional[datetime]:
        return self.completed_at


class TraceContainer(list):
    """List container that also exposes .steps and .event_id."""
    def __init__(self, items=None, event_id: Optional[str] = None):
        super().__init__(items or [])
        self.event_id = event_id

    @property
    def steps(self):
        return self


@dataclass
class PipelineContext:
    correlation_id: str
    event_id: str
    flow: Dict[str, Any]
    features: Dict[str, float]
    model_name: str
    source_domain: str = "nfton"
    
    threat: Optional[Any] = None
    explanation: Optional[Any] = None
    knowledge: Optional[Any] = None
    risk: Optional[Any] = None
    decision: Optional[Any] = None
    
    trace: TraceContainer = field(default_factory=TraceContainer)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    status: str = "running"
    error: Optional[str] = None
    working_memory: Optional[Any] = None
    shared_memory: Optional[Any] = None
    approval_token: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.trace, TraceContainer):
            self.trace = TraceContainer(self.trace, event_id=self.event_id)
        else:
            self.trace.event_id = self.event_id

        if self.working_memory is None:
            from argus.memory.working_memory import WorkingMemory
            self.working_memory = WorkingMemory(agent_id=self.correlation_id)

    def add_trace(self, event: TraceEvent):
        self.trace.append(event)

    @property
    def data_intelligence_result(self) -> Optional[Dict[str, Any]]:
        if not self.features:
            return None
        return {
            "status": "success",
            "features": self.features,
            "feature_count": len(self.features),
            "feature_source": getattr(self, "feature_source", "pre_computed"),
        }

    @property
    def threat_result(self) -> Optional[Any]:
        return self.threat

    @property
    def explainability_result(self) -> Optional[Any]:
        return self.explanation

    @property
    def knowledge_result(self) -> Optional[Any]:
        return self.knowledge

    @property
    def risk_result(self) -> Optional[Any]:
        return self.risk

    @property
    def decision_result(self) -> Optional[Any]:
        return self.decision


async def _step_data_intelligence(ctx: PipelineContext) -> None:
    from argus.agents.data_intelligence.agent import DataIntelligenceAgent
    from argus.agents.data_intelligence.schemas import FlowInput

    start_time = datetime.now(timezone.utc)
    try:
        agent = DataIntelligenceAgent()
        await agent.initialize()

        flow_input = FlowInput(
            correlation_id=ctx.correlation_id,
            event_id=ctx.event_id,
            source_domain=getattr(ctx, "source_domain", "nfton"),
            fields=ctx.flow,
        )
        result = await agent.process_flow(flow_input)

        if result.status != "success":
            raise ValueError(result.error.error if result.error else "DIA processing failed")

        ctx.features = result.features
        ctx.feature_source = result.feature_source

        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="DATA_INTELLIGENCE",
            status="SUCCESS",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            input_summary=f"fields: {len(flow_input.fields)} total",
            output_summary=f"features: {len(result.features)} total",
        ))
    except Exception as exc:
        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="DATA_INTELLIGENCE",
            status="FAILED",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            error=str(exc)
        ))
        raise


async def _step_threat_analysis(ctx: PipelineContext) -> None:
    from argus.agents.threat_analysis.agent import ThreatAnalysisAgent

    start_time = datetime.now(timezone.utc)
    try:
        if not model_registry.is_loaded:
            model_registry.load_all()

        agent = ThreatAnalysisAgent()
        await agent.initialize()

        feature_input = {
            "event_id": ctx.event_id,
            "correlation_id": ctx.correlation_id,
            "source": "data_intelligence",
            "features": ctx.features,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_version": ctx.model_name
        }

        reasoning = await agent.reason(feature_input)
        result = await agent.execute(reasoning)
        ctx.threat = result

        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="THREAT_ANALYSIS",
            status="SUCCESS",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            input_summary=f"event_id={ctx.event_id}, model={ctx.model_name}",
            output_summary=f"threat_level={result.threat_level.value}, confidence={result.confidence:.4f}",
            model_version=result.model_version
        ))
    except Exception as exc:
        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="THREAT_ANALYSIS",
            status="FAILED",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            error=str(exc)
        ))
        raise


async def _step_explainability(ctx: PipelineContext) -> None:
    from argus.agents.explainability.agent import ExplainabilityAgent
    
    start_time = datetime.now(timezone.utc)
    try:
        agent = ExplainabilityAgent()
        await agent.initialize()

        explain_input = {
            "event_id": ctx.event_id,
            "correlation_id": ctx.correlation_id,
            "features": ctx.features,
            "model_version": ctx.model_name
        }

        reasoning = await agent.reason(explain_input)
        result = await agent.execute(reasoning)
        
        ctx.explanation = result.model_dump()
        
        end_time = datetime.now(timezone.utc)
        
        if result.status == "available":
            ctx.add_trace(TraceEvent(
                agent="EXPLAINABILITY",
                status="SUCCESS",
                started_at=start_time,
                completed_at=end_time,
                duration=(end_time - start_time).total_seconds() * 1000,
                input_summary=f"model={ctx.model_name}",
                output_summary=f"top_feature={result.top_feature}, impact={result.top_feature_impact:.4f}",
                model_version=ctx.model_name
            ))
        else:
            ctx.add_trace(TraceEvent(
                agent="EXPLAINABILITY",
                status="FAILED",
                started_at=start_time,
                completed_at=end_time,
                duration=(end_time - start_time).total_seconds() * 1000,
                error=f"Explainability unavailable: {result.reason}"
            ))
            raise ValueError(f"Explainability unavailable: {result.reason}")

    except Exception as exc:
        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="EXPLAINABILITY",
            status="FAILED",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            error=str(exc)
        ))
        raise


async def _step_knowledge_context(ctx: PipelineContext) -> None:
    from argus.agents.knowledge_context.agent import KnowledgeContextAgent

    start_time = datetime.now(timezone.utc)
    try:
        agent = KnowledgeContextAgent()
        await agent.initialize()

        threat = ctx.threat
        attack_type = "dos" if (threat and threat.threat_level.value in ("critical", "high", "medium")) else "benign"

        kca_input = {
            "event_id": ctx.event_id,
            "correlation_id": ctx.correlation_id,
            "attack_type": attack_type,
            "severity": threat.confidence if threat else 0.0,
            "description": f"Predicted by {threat.model_version}" if threat else "unknown",
        }

        reasoning = await agent.reason(kca_input)
        plan = await agent.plan(reasoning)
        knowledge_event = await agent.execute(plan)
        
        ctx.knowledge = knowledge_event

        end_time = datetime.now(timezone.utc)
        mitre_count = len(knowledge_event.mitre_techniques) if knowledge_event.mitre_techniques else 0
        cve_count = len(knowledge_event.cves) if knowledge_event.cves else 0

        ctx.add_trace(TraceEvent(
            agent="KNOWLEDGE_CONTEXT",
            status="SUCCESS",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            input_summary=f"attack_type={attack_type}",
            output_summary=f"mitre={mitre_count}, cves={cve_count}, conf={knowledge_event.confidence:.2f}"
        ))

    except Exception as exc:
        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="KNOWLEDGE_CONTEXT",
            status="FAILED",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            error=str(exc)
        ))
        raise


async def _step_risk_prediction(ctx: PipelineContext) -> None:
    from argus.agents.risk_prediction.agent import RiskPredictionAgent
    from argus.agents.risk_prediction.models.schemas import (
        RiskAnalysisInput, KnowledgeContext, ThreatAnalysisResult as RPThreatInput
    )

    start_time = datetime.now(timezone.utc)
    try:
        agent = RiskPredictionAgent()
        await agent.initialize()

        threat = ctx.threat
        knowledge = ctx.knowledge
        
        evidence_dicts = [e.model_dump() for e in threat.evidence] if threat.evidence else []
        rp_threat = RPThreatInput(
            source_event_id=threat.source_event_id,
            threat_level=threat.threat_level.value,
            confidence=threat.confidence,
            evidence=evidence_dicts,
            recommended_actions=threat.recommended_actions,
            model_version=threat.model_version,
        )

        cve_ids = []
        if hasattr(knowledge, 'cves') and knowledge.cves:
            for c in knowledge.cves:
                if isinstance(c, dict):
                    cve_ids.append(c.get("id") or c.get("cve_id") or str(c))
                else:
                    cve_ids.append(str(c))

        affected_assets = knowledge.affected_assets if hasattr(knowledge, 'affected_assets') and knowledge.affected_assets else []
        asset_types = knowledge.asset_types if hasattr(knowledge, 'asset_types') and knowledge.asset_types else {}

        if not affected_assets:
            if "dest_ip" in ctx.flow:
                affected_assets = [ctx.flow["dest_ip"]]
                asset_types[ctx.flow["dest_ip"]] = "scada_server" if threat.threat_level.value in ("critical", "high") else "hmi"
            elif "device_id" in ctx.flow:
                affected_assets = [ctx.flow["device_id"]]
                asset_types[ctx.flow["device_id"]] = "scada_server"
            else:
                asset_id = "scada_server_01" if threat.threat_level.value in ("critical", "high") else "hmi_terminal_01"
                affected_assets = [asset_id]
                asset_types = {asset_id: "scada_server" if threat.threat_level.value in ("critical", "high") else "hmi"}

        kc = KnowledgeContext(
            affected_assets=affected_assets,
            asset_types=asset_types,
            known_vulnerabilities=cve_ids,
            related_incidents=[]
        )

        risk_input = RiskAnalysisInput(
            threat_event=rp_threat,
            knowledge_event=kc,
        )

        reasoning = await agent.reason(risk_input)
        plan = await agent.plan(reasoning)
        result = await agent.execute(plan)
        ctx.risk = result
        await agent.publish(result)

        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="RISK_PREDICTION",
            status="SUCCESS",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            input_summary=f"threat={threat.threat_level.value}",
            output_summary=f"risk={result.risk_score}, sev={result.severity}"
        ))

    except Exception as exc:
        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="RISK_PREDICTION",
            status="FAILED",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            error=str(exc)
        ))
        raise


async def _step_decision_support(ctx: PipelineContext) -> None:
    from argus.agents.decision_support.agent import DecisionSupportAgent
    from argus.agents.decision_support.models.schemas import (
        DecisionAnalysisInput, RiskEventInput, KnowledgeContextInput
    )

    start_time = datetime.now(timezone.utc)
    try:
        agent = DecisionSupportAgent()
        await agent.initialize()

        risk = ctx.risk
        knowledge = ctx.knowledge

        risk_input = RiskEventInput(
            source_event_id=risk.source_event_id,
            risk_score=risk.risk_score,
            severity=risk.severity,
            confidence=risk.confidence,
            asset_priority=risk.asset_priority.value if risk.asset_priority else None,
            impact_estimation=risk.impact_estimation.model_dump() if getattr(risk, 'impact_estimation', None) else None,
            reasoning=risk.reasoning,
            metadata=risk.metadata,
        )

        cve_ids = []
        if hasattr(knowledge, 'cves') and knowledge.cves:
            for c in knowledge.cves:
                if isinstance(c, dict):
                    cve_ids.append(c.get("id") or c.get("cve_id") or str(c))
                else:
                    cve_ids.append(str(c))

        affected_assets = knowledge.affected_assets if hasattr(knowledge, 'affected_assets') and knowledge.affected_assets else []
        asset_types = knowledge.asset_types if hasattr(knowledge, 'asset_types') and knowledge.asset_types else {}
        if not affected_assets:
            if "dest_ip" in ctx.flow:
                affected_assets = [ctx.flow["dest_ip"]]
                asset_types[ctx.flow["dest_ip"]] = "scada_server"
            elif "device_id" in ctx.flow:
                affected_assets = [ctx.flow["device_id"]]
                asset_types[ctx.flow["device_id"]] = "scada_server"
            else:
                asset_id = "scada_server_01" if (ctx.threat and ctx.threat.threat_level.value in ("critical", "high")) else "hmi_terminal_01"
                affected_assets = [asset_id]
                asset_types = {asset_id: "scada_server" if (ctx.threat and ctx.threat.threat_level.value in ("critical", "high")) else "hmi"}

        knowledge_input = KnowledgeContextInput(
            affected_assets=affected_assets,
            asset_types=asset_types,
            known_vulnerabilities=cve_ids,
            related_incidents=[]
        )

        decision_input = DecisionAnalysisInput(
            risk_event=risk_input,
            knowledge_event=knowledge_input,
        )

        reasoning = await agent.reason(decision_input)
        plan = await agent.plan(reasoning)
        result = await agent.execute(plan)
        ctx.decision = result

        rec_count = len(result.recommended_actions) if result.recommended_actions else 0
        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="DECISION_SUPPORT",
            status="SUCCESS",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            input_summary=f"risk={risk.risk_score}",
            output_summary=f"recs={rec_count}, pri={result.priority}"
        ))

    except Exception as exc:
        end_time = datetime.now(timezone.utc)
        ctx.add_trace(TraceEvent(
            agent="DECISION_SUPPORT",
            status="FAILED",
            started_at=start_time,
            completed_at=end_time,
            duration=(end_time - start_time).total_seconds() * 1000,
            error=str(exc)
        ))
        raise


async def execute_pipeline(
    features: Dict[str, float],
    model_name: str = "xgb_adapted",
    correlation_id: Optional[str] = None,
    source_domain: str = "nfton",
    stage_callback: Optional[Any] = None,
) -> PipelineContext:
    if correlation_id is None:
        correlation_id = f"flow-{uuid.uuid4().hex[:12]}"

    event_id = f"evt-{uuid.uuid4().hex[:8]}"

    ctx = PipelineContext(
        correlation_id=correlation_id,
        event_id=event_id,
        flow=features,
        features={},
        model_name=model_name,
        source_domain=source_domain,
    )

    async def _emit_stage_start(stage_name: str):
        if stage_callback:
            start_evt = {
                "stage": stage_name,
                "status": "RUNNING",
                "event_type": "stage_start",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "correlation_id": ctx.correlation_id,
                "event_id": ctx.event_id,
                "model_version": ctx.model_name,
            }
            if inspect.iscoroutinefunction(stage_callback):
                await stage_callback(start_evt)
            elif callable(stage_callback):
                stage_callback(start_evt)

    async def _emit_stage_end(trace_evt: TraceEvent):
        try:
            from argus.observability.metrics import metrics
            metrics.record_agent_execution(
                agent_name=trace_evt.agent,
                status=trace_evt.status,
                duration_ms=trace_evt.duration or 0.0,
            )
        except Exception as mexc:
            logger.warning("metrics_record_stage_failed", agent=trace_evt.agent, error=str(mexc))

        if stage_callback:
            end_evt = {
                "stage": trace_evt.agent,
                "status": trace_evt.status,
                "event_type": "stage_end",
                "started_at": trace_evt.started_at.isoformat() if trace_evt.started_at else None,
                "completed_at": trace_evt.completed_at.isoformat() if trace_evt.completed_at else None,
                "duration_ms": trace_evt.duration,
                "summary": trace_evt.output_summary or trace_evt.input_summary or f"{trace_evt.agent}: {trace_evt.status}",
                "input_summary": trace_evt.input_summary,
                "output_summary": trace_evt.output_summary,
                "error": trace_evt.error,
                "model_version": trace_evt.model_version or ctx.model_name,
                "correlation_id": ctx.correlation_id,
                "event_id": ctx.event_id,
            }
            if inspect.iscoroutinefunction(stage_callback):
                await stage_callback(end_evt)
            elif callable(stage_callback):
                stage_callback(end_evt)

    step_pipeline = [
        ("DATA_INTELLIGENCE", _step_data_intelligence),
        ("THREAT_ANALYSIS", _step_threat_analysis),
        ("EXPLAINABILITY", _step_explainability),
        ("KNOWLEDGE_CONTEXT", _step_knowledge_context),
        ("RISK_PREDICTION", _step_risk_prediction),
        ("DECISION_SUPPORT", _step_decision_support),
    ]

    try:
        for stage_name, step_fn in step_pipeline:
            await _emit_stage_start(stage_name)
            await step_fn(ctx)
            if ctx.trace:
                await _emit_stage_end(ctx.trace[-1])
        ctx.status = "completed"
    except Exception as e:
        ctx.status = "failed"
        ctx.error = str(e)
        if ctx.trace and ctx.trace[-1].status == "FAILED":
            await _emit_stage_end(ctx.trace[-1])
        
        # Add skipped traces for remaining steps
        steps = [
            ("DATA_INTELLIGENCE", ctx.features),
            ("THREAT_ANALYSIS", ctx.threat),
            ("EXPLAINABILITY", ctx.explanation),
            ("KNOWLEDGE_CONTEXT", ctx.knowledge),
            ("RISK_PREDICTION", ctx.risk),
            ("DECISION_SUPPORT", ctx.decision)
        ]
        
        for agent_name, result in steps:
            if result is None:
                # Check if it was already marked as FAILED in trace
                already_failed = any(t.agent == agent_name and t.status == "FAILED" for t in ctx.trace)
                if not already_failed:
                    skipped_trace = TraceEvent(
                        agent=agent_name,
                        status="SKIPPED",
                        error=f"Dependency failed: {e}"
                    )
                    ctx.add_trace(skipped_trace)
                    await _emit_stage_end(skipped_trace)
        
    ctx.completed_at = datetime.now(timezone.utc)
    try:
        from argus.orchestrator.store import pipeline_store
        ctx.approval_token = pipeline_store.persist_pipeline_run(ctx)
    except Exception as exc:
        logger.error("persist_pipeline_run_failed", error=str(exc))
    return ctx


def pipeline_context_to_response(ctx: PipelineContext) -> Dict[str, Any]:
    trace_events = []
    for step in ctx.trace:
        trace_events.append({
            "agent": step.agent,
            "status": step.status,
            "started_at": step.started_at.isoformat() if step.started_at else None,
            "completed_at": step.completed_at.isoformat() if step.completed_at else None,
            "duration": step.duration,
            "input_summary": step.input_summary,
            "output_summary": step.output_summary,
            "model_version": step.model_version,
            "error": step.error,
        })

    approval_required = bool(ctx.decision and getattr(ctx.decision, "approval_required", False))

    return {
        "correlation_id": ctx.correlation_id,
        "event_id": ctx.event_id,
        "status": ctx.status,
        "error": ctx.error,
        "approval_required": approval_required,
        "approval_token": ctx.approval_token,
        "started_at": ctx.started_at.isoformat(),
        "completed_at": ctx.completed_at.isoformat() if ctx.completed_at else None,
        "total_duration_ms": round(
            (ctx.completed_at - ctx.started_at).total_seconds() * 1000, 2
        ) if ctx.completed_at else None,
        "features": ctx.features,
        "model_name": ctx.model_name,
        "results": {
            "data_intelligence": bool(ctx.features),
            "threat_analysis": bool(ctx.threat),
            "explainability": bool(ctx.explanation),
            "knowledge_context": bool(ctx.knowledge),
            "risk_prediction": bool(ctx.risk),
            "decision_support": bool(ctx.decision),
        },
        "trace": {
            "event_id": ctx.event_id,
            "total_steps": len(ctx.trace),
            "steps": trace_events,
        },
    }
