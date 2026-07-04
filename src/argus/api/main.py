"""FastAPI application entry point."""
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from structlog import get_logger
import uvicorn
from contextlib import asynccontextmanager

from config.settings import get_settings
from argus.security.middleware import SecurityMiddleware
from argus.api.routers import agents, tasks
from argus.schemas.health import SystemHealth

logger = get_logger("argus.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB, Bus, Blackboard, Orchestrator
    logger.info("api_startup")
    yield
    # Shutdown: Cleanup resources
    logger.info("api_shutdown")

app = FastAPI(
    title="ARGUS Platform API",
    description="Autonomous Risk-aware Grid Understanding & Security",
    version="0.1.0",
    lifespan=lifespan
)

settings = get_settings()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityMiddleware)

# Routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])

@app.get("/health", response_model=SystemHealth)
async def health_check():
    """System health check endpoint."""
    return SystemHealth(status="healthy", uptime=100.0, timestamp="2025-01-01T00:00:00Z")

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time SOC dashboard updates."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WS messages
    except WebSocketDisconnect:
        logger.info("websocket_disconnected")

if __name__ == "__main__":
    uvicorn.run("argus.api.main:app", host=settings.host, port=settings.port, reload=settings.debug)
