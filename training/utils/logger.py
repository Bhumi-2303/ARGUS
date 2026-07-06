import logging
import structlog
from pathlib import Path
from typing import Any, Dict

def setup_logging(config: Dict[str, Any]) -> None:
    """Configures structured logging for the training framework."""
    log_level_str = config.get("logging", {}).get("level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Ensure log directory exists if file logging is enabled
    if config.get("logging", {}).get("file", False):
        log_dir = Path(config.get("logging", {}).get("log_dir", "training/logs/"))
        log_dir.mkdir(parents=True, exist_ok=True)
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if config.get("logging", {}).get("structured", True) else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """Gets a structlog logger instance."""
    return structlog.get_logger(name)
