"""Streaming pipeline endpoint utilizing MessageBus and SSE / WebSocket."""

import os
import json
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional, List
import pandas as pd
from fastapi import APIRouter, Query, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import structlog

from argus.schemas.api import StreamEventPayload, ModelPredictionDetail
from argus.registry.model_registry import model_registry, HARMONIZED_FEATURES
from argus.bus.message_bus import MessageBus

logger = structlog.get_logger("argus.stream")

router = APIRouter()

# Shared message bus instance for streaming pipeline
global_bus = MessageBus()


async def stream_generator(domain: str, model_names: List[str], speed: float, seed: int):
    """Async generator streaming events replaying verified domain telemetry via MessageBus."""
    sample_path = f"data/samples/{domain}.parquet"
    if not os.path.exists(sample_path):
        err_msg = json.dumps({"error": f"Verified telemetry sample for domain '{domain}' not found at '{sample_path}'"})
        yield f"event: error\ndata: {err_msg}\n\n"
        return



    df = pd.read_parquet(sample_path)
    if seed is not None:
        df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    delay = 1.0 / max(0.1, speed)
    logger.info("stream_started", domain=domain, models=model_names, speed=speed, rows=len(df))

    for idx, row in df.iterrows():
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

        # Publish event to existing MessageBus
        if global_bus._running:
            await global_bus.publish("stream.events", event_payload)

        # Yield SSE event format
        yield f"data: {json.dumps(event_payload)}\n\n"
        await asyncio.sleep(delay)


@router.get("/stream", tags=["stream"])
async def get_stream(
    domain: str = Query("nfton", description="Target domain: ciciot, nfton, iec104"),
    models: str = Query("model_d2_coral,xgb_source", description="Comma-separated list of models to evaluate"),
    speed: float = Query(10.0, description="Replay speed in flows/sec"),
    seed: int = Query(42, description="Random seed for flow sampling")
):
    """Server-Sent Events (SSE) stream replaying flows at controllable speed."""
    model_list = [m.strip() for m in models.split(",") if m.strip()]
    if not model_list:
        model_list = ["model_d2_coral"]

    return StreamingResponse(
        stream_generator(domain=domain, model_names=model_list, speed=speed, seed=seed),
        media_type="text/event-stream"
    )


@router.websocket("/stream/ws")
async def websocket_stream(
    websocket: WebSocket,
    domain: str = "nfton",
    models: str = "model_d2_coral,xgb_source",
    speed: float = 10.0,
    seed: int = 42
):
    """WebSocket endpoint for real-time flow streaming."""
    await websocket.accept()
    model_list = [m.strip() for m in models.split(",") if m.strip()]
    if not model_list:
        model_list = ["model_d2_coral"]

    try:
        async for sse_chunk in stream_generator(domain=domain, model_names=model_list, speed=speed, seed=seed):
            if sse_chunk.startswith("data: "):
                payload_str = sse_chunk[6:].strip()
                await websocket.send_text(payload_str)
    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected")
    except Exception as ex:
        logger.error("websocket_stream_error", error=str(ex))
        await websocket.close()
