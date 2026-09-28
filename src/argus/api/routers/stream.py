"""Streaming pipeline endpoint utilizing MessageBus, SSE, and authenticated WebSockets."""

import os
import json
import time
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional, List
import pandas as pd
from fastapi import APIRouter, Query, HTTPException, status, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.responses import StreamingResponse
from structlog import get_logger

from configs.settings import get_settings
from argus.schemas.api import StreamEventPayload, ModelPredictionDetail
from argus.registry.model_registry import model_registry, HARMONIZED_FEATURES, MODEL_METADATA
from argus.bus.message_bus import MessageBus
from argus.auth.rbac import get_current_user, require_permission
from argus.auth.models import UserPrincipal
from argus.auth.jwt import jwt_validator
from argus.data.manager import ALLOWED_DOMAINS

logger = get_logger("argus.stream")

router = APIRouter()

# Shared message bus instance for streaming pipeline
global_bus = MessageBus()

MAX_STREAM_ROWS = 1000
MAX_STREAM_DURATION_SECONDS = 300  # 5 minutes


def _validate_origin(origin: Optional[str], allowed_origins: List[str], is_prod: bool) -> bool:
    """Validate WebSocket origin against configured CORS allowlist."""
    if not origin:
        # In production, require origin header
        return not is_prod
    origin_clean = origin.rstrip("/")
    for allowed in allowed_origins:
        if allowed == "*" or allowed.rstrip("/") == origin_clean:
            return True
    return False


async def stream_generator(
    domain: str,
    model_names: List[str],
    speed: float,
    seed: int,
    request: Optional[Request] = None
):
    """Async generator streaming events replaying verified domain telemetry with bounds checking."""
    if domain not in ALLOWED_DOMAINS:
        err_msg = json.dumps({"error": f"Invalid domain '{domain}'. Allowed: {sorted(ALLOWED_DOMAINS)}"})
        yield f"event: error\ndata: {err_msg}\n\n"
        return

    sample_path = f"data/samples/{domain}.parquet"
    if not os.path.exists(sample_path):
        err_msg = json.dumps({"error": f"Telemetry sample for domain '{domain}' not found."})
        yield f"event: error\ndata: {err_msg}\n\n"
        return

    df = pd.read_parquet(sample_path)
    if seed is not None:
        df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    delay = 1.0 / max(0.1, min(100.0, speed))
    logger.info("stream_started", domain=domain, models=model_names, speed=speed, rows=min(len(df), MAX_STREAM_ROWS))

    start_time = time.time()
    count = 0

    for idx, row in df.iterrows():
        # Check client disconnect or max bounds
        if request and await request.is_disconnected():
            logger.info("stream_client_disconnected", domain=domain, count=count)
            break

        if count >= MAX_STREAM_ROWS or (time.time() - start_time) > MAX_STREAM_DURATION_SECONDS:
            logger.info("stream_bounds_reached", domain=domain, count=count)
            break

        feat_dict = {col: float(row[col]) for col in HARMONIZED_FEATURES}
        true_label = int(row["label"]) if "label" in row else 0

        predictions_detail = {}
        for m_name in model_names:
            try:
                prob, pred_lbl, _ = model_registry.predict(m_name, feat_dict)
                predictions_detail[m_name] = ModelPredictionDetail(
                    probability=round(prob, 6),
                    label=pred_lbl
                ).model_dump()
            except Exception:
                predictions_detail[m_name] = ModelPredictionDetail(
                    probability=0.50,
                    label=0
                ).model_dump()

        event_payload = {
            "event_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": domain,
            "features": feat_dict,
            "true_label": true_label,
            "predictions": predictions_detail
        }

        # Publish event to MessageBus
        if global_bus._running:
            await global_bus.publish("stream.events", event_payload)

        # Yield SSE event format
        yield f"data: {json.dumps(event_payload)}\n\n"
        count += 1
        await asyncio.sleep(delay)


@router.get("/stream", tags=["stream"])
async def get_stream(
    request: Request,
    domain: str = Query("nfton", description="Target domain: ciciot, nfton, iec104"),
    models: str = Query("model_d2_coral,xgb_source", description="Comma-separated list of models to evaluate"),
    speed: float = Query(10.0, ge=0.1, le=100.0, description="Replay speed in flows/sec"),
    seed: int = Query(42, ge=0, le=2147483647, description="Random seed for flow sampling"),
    user: UserPrincipal = Depends(require_permission("read:telemetry")),
):
    """Server-Sent Events (SSE) stream replaying verified flows at controllable speed with RBAC."""
    if domain not in ALLOWED_DOMAINS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid domain '{domain}'. Allowed domains: {sorted(ALLOWED_DOMAINS)}"
        )

    model_list = [m.strip() for m in models.split(",") if m.strip()]
    if not model_list:
        model_list = ["model_d2_coral"]

    # Validate model names
    known_models = set(model_registry.loaded_models.keys()) | set(MODEL_METADATA.keys())
    for m in model_list:
        if m not in known_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model '{m}'. Registered models: {sorted(known_models)}"
            )

    return StreamingResponse(
        stream_generator(domain=domain, model_names=model_list, speed=speed, seed=seed, request=request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no"
        }
    )


@router.websocket("/stream/ws")
async def websocket_stream(
    websocket: WebSocket,
    domain: str = "nfton",
    models: str = "model_d2_coral,xgb_source",
    speed: float = 10.0,
    seed: int = 42,
    token: Optional[str] = None
):
    """WebSocket endpoint for real-time flow streaming with origin check and authentication."""
    settings = get_settings()

    # 1. Validate Origin
    origin = websocket.headers.get("origin")
    if not _validate_origin(origin, settings.security.cors_origins, settings.is_production):
        logger.warning("websocket_origin_rejected", origin=origin)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Authenticate WebSocket Connection
    if settings.is_production or settings.security.oidc_enabled or token:
        if not token:
            # Check Authorization header in websocket if present
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header[7:].strip()

        if not token:
            logger.warning("websocket_unauthenticated", path="/stream/ws")
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
    if domain not in ALLOWED_DOMAINS:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return

    speed = max(0.1, min(100.0, float(speed)))
    model_list = [m.strip() for m in models.split(",") if m.strip()]
    if not model_list:
        model_list = ["model_d2_coral"]

    await websocket.accept()

    try:
        start_time = time.time()
        max_duration = settings.security.max_websocket_duration_seconds

        async for sse_chunk in stream_generator(domain=domain, model_names=model_list, speed=speed, seed=seed):
            if (time.time() - start_time) > max_duration:
                logger.info("websocket_duration_limit_reached")
                break
            if sse_chunk.startswith("data: "):
                payload_str = sse_chunk[6:].strip()
                await websocket.send_text(payload_str)

    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected")
    except Exception as ex:
        logger.error("websocket_stream_error", error=str(ex))
        try:
            await websocket.close()
        except Exception:
            pass
