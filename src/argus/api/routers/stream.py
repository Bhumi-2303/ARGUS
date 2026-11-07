"""Streaming pipeline endpoint utilizing MessageBus, SSE, and authenticated WebSockets.

Provides verified flow replay replaying rows from dataset/*.parquet through the real
6-agent ARGUS pipeline at configurable rates with interactive controls (pause/resume/speed/domain/seed),
per-stage trace event emission, and strict RBAC enforcement.
"""

import os
import json
import time
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import pandas as pd
from fastapi import (
    APIRouter,
    Query,
    HTTPException,
    status,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    Request,
)
from fastapi.responses import StreamingResponse
from structlog import get_logger

from configs.settings import get_settings
from argus.schemas.api import ModelPredictionDetail
from argus.registry.model_registry import model_registry, HARMONIZED_FEATURES, MODEL_METADATA
from argus.bus.message_bus import MessageBus
from argus.auth.rbac import require_permission
from argus.auth.models import UserPrincipal
from argus.auth.jwt import jwt_validator
from argus.data.manager import ALLOWED_DOMAINS
from argus.orchestrator.pipeline import execute_pipeline

logger = get_logger("argus.stream")

router = APIRouter(tags=["stream", "verified-flow-replay"])

# Shared message bus instance for streaming pipeline
global_bus = MessageBus()

MAX_STREAM_ROWS = 1000
MAX_STREAM_DURATION_SECONDS = 300  # 5 minutes
MAX_WS_MESSAGE_SIZE = 32768  # 32 KB limit for incoming frames

STREAM_METADATA_LABEL = "verified flow replay"

STAGE_NODES: Dict[str, tuple[str, str]] = {
    "DATA_INTELLIGENCE": ("orchestrator", "data_intelligence"),
    "THREAT_ANALYSIS": ("data_intelligence", "threat_analysis"),
    "EXPLAINABILITY": ("threat_analysis", "explainability"),
    "KNOWLEDGE_CONTEXT": ("threat_analysis", "knowledge_context"),
    "RISK_PREDICTION": ("knowledge_context", "risk_prediction"),
    "DECISION_SUPPORT": ("risk_prediction", "decision_support"),
}


def normalize_domain_name(domain: str) -> str:
    """Normalize domain strings to canonical values (ciciot, nfton, iec104)."""
    d = domain.strip().lower()
    if d in ("ciciot", "ciciot2023", "cic"):
        return "ciciot"
    if d in ("nfton", "nf-ton", "toniot", "ton"):
        return "nfton"
    if d in ("iec104", "iec-104", "iec"):
        return "iec104"
    return d


def load_replay_dataframe(domain: str, seed: Optional[int] = None) -> pd.DataFrame:
    """Load telemetry parquet dataframe from dataset/*.parquet with fallback to data/samples."""
    norm_dom = normalize_domain_name(domain)
    primary_path = f"dataset/{norm_dom}.parquet"
    fallback_path = f"data/samples/{norm_dom}.parquet"
    path = primary_path if os.path.exists(primary_path) else fallback_path

    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset for domain '{domain}' not found at '{path}'")

    df = pd.read_parquet(path)
    if seed is not None:
        df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def _validate_origin(origin: Optional[str], allowed_origins: List[str], is_prod: bool) -> bool:
    """Validate WebSocket origin against configured CORS allowlist."""
    if not origin:
        return not is_prod
    origin_clean = origin.rstrip("/")
    for allowed in allowed_origins:
        if allowed == "*" or allowed.rstrip("/") == origin_clean:
            return True
    return False


def build_stage_event_payload(
    stage_event: Dict[str, Any],
    flow_idx: int,
    domain: str,
) -> Dict[str, Any]:
    """Format per-stage events matching both TraceEvent and FlowEventItem schemas."""
    stage = stage_event.get("stage", "UNKNOWN")
    src_node, tgt_node = STAGE_NODES.get(stage, ("orchestrator", stage.lower()))

    summary = stage_event.get("summary") or f"{stage}: {stage_event.get('status')}"
    duration_ms = stage_event.get("duration_ms")

    payload = {
        "stage": stage,
        "status": stage_event.get("status"),
        "duration_ms": duration_ms,
        "input": stage_event.get("input_summary"),
        "output": stage_event.get("output_summary"),
        "model_version": stage_event.get("model_version"),
        "error": stage_event.get("error"),
    }

    event_item = {
        "event_id": stage_event.get("event_id") or str(uuid.uuid4())[:8],
        "correlation_id": stage_event.get("correlation_id", ""),
        "source_node": src_node,
        "target_node": tgt_node,
        "event_type": stage_event.get("event_type", "stage_end"),
        "timestamp": stage_event.get("completed_at")
        or stage_event.get("started_at")
        or datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "payload": payload,
    }

    return {
        "type": "flow_event",
        "stream_type": STREAM_METADATA_LABEL,
        "flow_index": flow_idx,
        "domain": domain,
        "stage": stage,
        "event_type": stage_event.get("event_type", "stage_end"),
        "status": stage_event.get("status"),
        "duration_ms": duration_ms,
        "started_at": stage_event.get("started_at"),
        "completed_at": stage_event.get("completed_at"),
        "input_summary": stage_event.get("input_summary"),
        "output_summary": stage_event.get("output_summary"),
        "summary": summary,
        "error": stage_event.get("error"),
        "model_version": stage_event.get("model_version"),
        "event": event_item,
    }


class ReplayStreamControl:
    """Thread-safe state container for interactive stream replay controls."""

    def __init__(
        self,
        speed: float = 1.0,
        domain: str = "nfton",
        seed: int = 42,
        model_name: str = "model_d2_coral",
    ):
        self.is_paused = False
        self.pause_event = asyncio.Event()
        self.pause_event.set()
        self.speed = max(0.1, min(100.0, float(speed)))
        self.domain = domain
        self.seed = seed
        self.model_name = model_name
        self.reload_requested = False
        self.active = True

    def set_paused(self, paused: bool):
        self.is_paused = paused
        if paused:
            self.pause_event.clear()
        else:
            self.pause_event.set()

    def set_speed(self, speed: float):
        self.speed = max(0.1, min(100.0, float(speed)))

    def set_domain(self, domain: str):
        self.domain = domain
        self.reload_requested = True

    def set_seed(self, seed: int):
        self.seed = seed
        self.reload_requested = True


async def stream_generator(
    domain: str,
    model_names: List[str],
    speed: float,
    seed: int,
    request: Optional[Request] = None,
    rows: Optional[int] = None,
):
    """Async generator streaming events replaying verified domain telemetry with bounds checking."""
    norm_dom = normalize_domain_name(domain)
    if norm_dom not in ALLOWED_DOMAINS:
        err_msg = json.dumps(
            {"error": f"Invalid domain '{domain}'. Allowed: {sorted(ALLOWED_DOMAINS)}"}
        )
        yield f"event: error\ndata: {err_msg}\n\n"
        return

    try:
        df = load_replay_dataframe(norm_dom, seed=seed)
    except FileNotFoundError:
        err_msg = json.dumps({"error": f"Telemetry sample for domain '{domain}' not found."})
        yield f"event: error\ndata: {err_msg}\n\n"
        return

    max_rows = min(rows, MAX_STREAM_ROWS) if rows is not None else MAX_STREAM_ROWS
    delay = 1.0 / max(0.1, min(100.0, speed))
    logger.info(
        "stream_started",
        stream_type=STREAM_METADATA_LABEL,
        domain=norm_dom,
        models=model_names,
        speed=speed,
        rows=min(len(df), max_rows),
    )

    start_time = time.time()
    count = 0

    for _idx, row in df.iterrows():
        if request and await request.is_disconnected():
            logger.info("stream_client_disconnected", domain=norm_dom, count=count)
            break

        if count >= max_rows or (time.time() - start_time) > MAX_STREAM_DURATION_SECONDS:
            logger.info("stream_bounds_reached", domain=norm_dom, count=count)
            break

        feat_dict = {col: float(row[col]) for col in HARMONIZED_FEATURES}
        true_label = int(row["label"]) if "label" in row and pd.notna(row["label"]) else 0

        predictions_detail = {}
        for m_name in model_names:
            try:
                expected_feats = model_registry.get_expected_features(m_name)
                m_feat_dict = {col: float(row[col]) for col in expected_feats}
                prob, pred_lbl, _ = model_registry.predict(m_name, m_feat_dict)
                predictions_detail[m_name] = ModelPredictionDetail(
                    probability=round(prob, 6), label=pred_lbl
                ).model_dump()
            except Exception as ex:
                logger.warning("stream_inference_failed", model=m_name, error=str(ex))
                predictions_detail[m_name] = ModelPredictionDetail(
                    probability=0.50, label=0
                ).model_dump()

        event_payload = {
            "event_id": str(uuid.uuid4())[:8],
            "stream_type": STREAM_METADATA_LABEL,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": norm_dom,
            "features": feat_dict,
            "true_label": true_label,
            "predictions": predictions_detail,
        }

        if global_bus._running:
            await global_bus.publish("stream.events", event_payload)

        yield f"data: {json.dumps(event_payload)}\n\n"
        count += 1
        await asyncio.sleep(delay)


@router.get(
    "/stream",
    tags=["stream", "verified-flow-replay"],
    summary="Verified Flow Replay SSE Stream",
    description="Server-Sent Events (SSE) stream providing verified flow replay of domain telemetry at controllable speed with RBAC.",
)
async def get_stream(
    request: Request,
    domain: str = Query("nfton", description="Target domain: ciciot, nfton, iec104"),
    models: str = Query(
        "model_d2_coral,xgb_source", description="Comma-separated list of models to evaluate"
    ),
    speed: float = Query(10.0, ge=0.1, le=100.0, description="Replay speed in flows/sec"),
    seed: int = Query(42, ge=0, le=2147483647, description="Random seed for flow sampling"),
    rows: Optional[int] = Query(None, ge=1, le=1000, description="Max rows to stream"),
    user: UserPrincipal = Depends(require_permission("read:telemetry")),
):
    norm_dom = normalize_domain_name(domain)
    if norm_dom not in ALLOWED_DOMAINS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid domain '{domain}'. Allowed domains: {sorted(ALLOWED_DOMAINS)}",
        )

    model_list = [m.strip() for m in models.split(",") if m.strip()]
    if not model_list:
        model_list = ["model_d2_coral"]

    known_models = set(model_registry.loaded_models.keys()) | set(MODEL_METADATA.keys())
    for m in model_list:
        if m not in known_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model '{m}'. Registered models: {sorted(known_models)}",
            )

    return StreamingResponse(
        stream_generator(
            domain=norm_dom,
            model_names=model_list,
            speed=speed,
            seed=seed,
            request=request,
            rows=rows,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "X-Stream-Type": STREAM_METADATA_LABEL,
        },
    )


async def _handle_replay_stream_ws(
    websocket: WebSocket,
    domain: str = "nfton",
    models: str = "model_d2_coral",
    speed: float = 1.0,
    seed: int = 42,
    token: Optional[str] = None,
):
    """Internal WebSocket handler running verified flow replay through the 6-agent pipeline."""
    settings = get_settings()

    # 1. Validate Origin
    origin = websocket.headers.get("origin")
    if not _validate_origin(origin, settings.security.cors_origins, settings.is_production):
        logger.warning("websocket_origin_rejected", origin=origin)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Authenticate WebSocket Connection & Enforce RBAC
    if settings.is_production or settings.security.oidc_enabled or token:
        if not token:
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header[7:].strip()

        if not token:
            logger.warning("websocket_unauthenticated", path="/api/v1/stream")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            user = await jwt_validator.validate_token(token)
            if not user.has_permission("read:telemetry"):
                logger.warning("websocket_forbidden", user=user.sub, perm="read:telemetry")
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except Exception as e:
            logger.warning("websocket_auth_failed", error=str(e))
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    # 3. Validate Inputs
    norm_domain = normalize_domain_name(domain)
    if norm_domain not in ALLOWED_DOMAINS:
        logger.warning("websocket_invalid_domain", domain=domain)
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return

    model_name = models.split(",")[0].strip() if models else "model_d2_coral"

    # Pre-check dataset existence
    try:
        initial_df = load_replay_dataframe(norm_domain, seed=seed)
    except FileNotFoundError:
        logger.warning("websocket_dataset_not_found", domain=norm_domain)
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return

    await websocket.accept()

    ctrl = ReplayStreamControl(speed=speed, domain=norm_domain, seed=seed, model_name=model_name)

    # Handshake: Send stream_init event labeled "verified flow replay"
    init_payload = {
        "type": "stream_init",
        "stream_type": STREAM_METADATA_LABEL,
        "label": STREAM_METADATA_LABEL,
        "domain": ctrl.domain,
        "speed": ctrl.speed,
        "seed": ctrl.seed,
        "model": ctrl.model_name,
        "total_rows": len(initial_df),
        "status": "ready",
    }
    await websocket.send_json(init_payload)

    # 4. Message Receiver Loop (Controls: pause/resume/speed/domain/seed + message size limit)
    async def message_receiver():
        try:
            while ctrl.active:
                raw_text = await websocket.receive_text()

                # Enforce message size limit (32 KB)
                if len(raw_text.encode("utf-8")) > MAX_WS_MESSAGE_SIZE:
                    logger.warning(
                        "websocket_message_size_exceeded", size=len(raw_text.encode("utf-8"))
                    )
                    await websocket.close(
                        code=status.WS_1009_MESSAGE_TOO_BIG,
                        reason="Message size exceeds 32KB limit",
                    )
                    ctrl.active = False
                    break

                try:
                    data = json.loads(raw_text)
                except Exception:
                    cmd = raw_text.strip().lower()
                    if cmd == "pause":
                        data = {"action": "pause"}
                    elif cmd == "resume":
                        data = {"action": "resume"}
                    else:
                        continue

                action = data.get("action") or data.get("type") or data.get("command")

                if action == "pause":
                    ctrl.set_paused(True)
                    await websocket.send_json(
                        {
                            "type": "control_ack",
                            "stream_type": STREAM_METADATA_LABEL,
                            "action": "pause",
                            "status": "paused",
                        }
                    )
                elif action == "resume":
                    ctrl.set_paused(False)
                    await websocket.send_json(
                        {
                            "type": "control_ack",
                            "stream_type": STREAM_METADATA_LABEL,
                            "action": "resume",
                            "status": "running",
                        }
                    )
                elif action == "speed":
                    val = float(data.get("value", data.get("speed", 1.0)))
                    ctrl.set_speed(val)
                    await websocket.send_json(
                        {
                            "type": "control_ack",
                            "stream_type": STREAM_METADATA_LABEL,
                            "action": "speed",
                            "speed": ctrl.speed,
                        }
                    )
                elif action == "domain":
                    target_dom = normalize_domain_name(
                        str(data.get("value", data.get("domain", "")))
                    )
                    if target_dom in ALLOWED_DOMAINS:
                        ctrl.set_domain(target_dom)
                        await websocket.send_json(
                            {
                                "type": "control_ack",
                                "stream_type": STREAM_METADATA_LABEL,
                                "action": "domain",
                                "domain": ctrl.domain,
                            }
                        )
                elif action == "seed":
                    new_seed = int(data.get("value", data.get("seed", 42)))
                    ctrl.set_seed(new_seed)
                    await websocket.send_json(
                        {
                            "type": "control_ack",
                            "stream_type": STREAM_METADATA_LABEL,
                            "action": "seed",
                            "seed": ctrl.seed,
                        }
                    )
        except WebSocketDisconnect:
            ctrl.active = False
        except Exception as exc:
            logger.warning("websocket_message_receiver_exit", error=str(exc))
            ctrl.active = False

    # 5. Stream Replay Loop through 6-agent pipeline
    async def flow_replayer():
        try:
            current_df = initial_df
            row_idx = 0
            total_replayed = 0

            while ctrl.active and total_replayed < MAX_STREAM_ROWS:
                # Handle pause
                await ctrl.pause_event.wait()
                if not ctrl.active:
                    break

                # Reload dataset if domain or seed changed
                if ctrl.reload_requested:
                    ctrl.reload_requested = False
                    try:
                        current_df = load_replay_dataframe(ctrl.domain, seed=ctrl.seed)
                        row_idx = 0
                    except Exception as ex:
                        logger.error("dataset_reload_failed", domain=ctrl.domain, error=str(ex))

                if row_idx >= len(current_df):
                    row_idx = 0

                row = current_df.iloc[row_idx]
                row_idx += 1
                total_replayed += 1

                feat_dict = {col: float(row[col]) for col in HARMONIZED_FEATURES}
                true_label = int(row["label"]) if "label" in row and pd.notna(row["label"]) else 0

                current_flow_idx = total_replayed

                # Callback to emit per-stage events as they execute
                async def on_stage_event(
                    stage_evt: Dict[str, Any], flow_idx: int = current_flow_idx
                ):
                    if not ctrl.active:
                        return
                    stage_payload = build_stage_event_payload(
                        stage_event=stage_evt, flow_idx=flow_idx, domain=ctrl.domain
                    )
                    await websocket.send_json(stage_payload)

                # Execute full 6-agent pipeline
                ctx = await execute_pipeline(
                    features=feat_dict,
                    model_name=ctrl.model_name,
                    source_domain=ctrl.domain,
                    stage_callback=on_stage_event,
                )

                # Emit flow_completed summary event
                if ctrl.active:
                    completed_payload = {
                        "type": "flow_completed",
                        "stream_type": STREAM_METADATA_LABEL,
                        "flow_index": total_replayed,
                        "correlation_id": ctx.correlation_id,
                        "event_id": ctx.event_id,
                        "domain": ctrl.domain,
                        "status": ctx.status,
                        "features": feat_dict,
                        "true_label": true_label,
                        "total_stages": len(ctx.trace),
                        "approval_required": getattr(ctx.decision, "approval_required", False)
                        if ctx.decision
                        else False,
                        "approval_token": ctx.approval_token,
                    }
                    await websocket.send_json(completed_payload)

                delay = 1.0 / max(0.1, ctrl.speed)
                await asyncio.sleep(delay)
        except WebSocketDisconnect:
            ctrl.active = False
        except Exception as exc:
            logger.error("flow_replayer_error", error=str(exc))
            ctrl.active = False

    # Run receiver and replayer concurrently
    receiver_task = asyncio.create_task(message_receiver())
    replayer_task = asyncio.create_task(flow_replayer())

    done, pending = await asyncio.wait(
        [receiver_task, replayer_task], return_when=asyncio.FIRST_COMPLETED
    )

    ctrl.active = False
    for task in pending:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, WebSocketDisconnect):
            pass


@router.websocket("/stream")
async def websocket_stream(
    websocket: WebSocket,
    domain: str = "nfton",
    models: str = "model_d2_coral",
    speed: float = 1.0,
    seed: int = 42,
    token: Optional[str] = None,
):
    """WebSocket endpoint providing verified flow replay of network flows through the 6-agent ARGUS pipeline."""
    await _handle_replay_stream_ws(websocket, domain, models, speed, seed, token)


@router.websocket("/stream/ws")
async def websocket_stream_ws(
    websocket: WebSocket,
    domain: str = "nfton",
    models: str = "model_d2_coral",
    speed: float = 1.0,
    seed: int = 42,
    token: Optional[str] = None,
):
    """Backward-compatible WebSocket endpoint for verified flow replay."""
    await _handle_replay_stream_ws(websocket, domain, models, speed, seed, token)
