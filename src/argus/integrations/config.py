"""Configuration for optional ARGUS agent runtime integrations (ADK & MCP)."""

import os
from typing import Optional
from pydantic import BaseModel, Field


class AgentRuntimeConfig(BaseModel):
    """Runtime configuration for optional external agent integration layers.

    IMPORTANT SAFETY CONSTRAINTS:
    - This layer is OFF by default.
    - This layer is NEVER on the detection path or decision execution path.
    - The core ARGUS detection, ML inference, risk scoring, and decision support
      remain 100% deterministic and rule/model-based.
    - This layer provides only read-only inspection tools (MCP) and post-incident
      narration (ADK/LLM) that summarize already-computed outputs.
    """

    enabled: bool = Field(
        default=False,
        description="Master switch for optional agent runtime integrations. OFF by default.",
    )
    mcp_server_enabled: bool = Field(
        default=False, description="Enable read-only MCP server exposing inspection tools."
    )
    adk_narrator_enabled: bool = Field(
        default=False,
        description="Enable optional LLM analyst narrator summarizing computed incident outputs.",
    )
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for live LLM narration. Cleanly degrades when unset.",
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash", description="Gemini model identifier for incident narration."
    )
    llm_timeout_seconds: float = Field(
        default=5.0,
        description="Timeout for LLM API calls before falling back to deterministic narration.",
    )


def get_runtime_config() -> AgentRuntimeConfig:
    """Load agent runtime configuration from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    enabled = os.getenv("ARGUS_AGENT_RUNTIME", "").lower() in ("true", "1", "yes")
    mcp_enabled = os.getenv("ARGUS_MCP_SERVER", "").lower() in ("true", "1", "yes") or enabled
    narrator_enabled = (
        os.getenv("ARGUS_ADK_NARRATOR", "").lower() in ("true", "1", "yes") or enabled
    )

    return AgentRuntimeConfig(
        enabled=enabled,
        mcp_server_enabled=mcp_enabled,
        adk_narrator_enabled=narrator_enabled,
        gemini_api_key=api_key,
        gemini_model=os.getenv("ARGUS_GEMINI_MODEL", "gemini-2.5-flash"),
        llm_timeout_seconds=float(os.getenv("ARGUS_LLM_TIMEOUT", "5.0")),
    )
