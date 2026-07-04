"""Retry policies and circuit breakers."""
from dataclasses import dataclass
import time
from typing import Callable, Any, Type
import asyncio
import structlog

logger = structlog.get_logger("argus.orchestrator.retry")

@dataclass
class RetryPolicy:
    """Policy for retrying failed operations."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0


class ExponentialBackoff:
    """Calculates delay for exponential backoff."""
    @staticmethod
    def calculate_delay(attempt: int, policy: RetryPolicy) -> float:
        delay = policy.base_delay * (policy.backoff_factor ** (attempt - 1))
        return min(delay, policy.max_delay)


class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0, half_open_max_calls: int = 2):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._state = "CLOSED" # CLOSED, OPEN, HALF_OPEN
        self._failures = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0
        
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function protected by the circuit breaker."""
        self._check_state()
        
        if self._state == "OPEN":
            raise Exception("Circuit breaker is OPEN")
            
        if self._state == "HALF_OPEN":
            self._half_open_calls += 1
            if self._half_open_calls > self.half_open_max_calls:
                raise Exception("Circuit breaker is HALF_OPEN and max test calls reached")
                
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
                
            # Success
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
            
    def _check_state(self) -> None:
        if self._state == "OPEN":
            if time.time() - self._last_failure_time > self.recovery_timeout:
                logger.info("circuit_breaker_half_open")
                self._state = "HALF_OPEN"
                self._half_open_calls = 0
                
    def _on_success(self) -> None:
        if self._state == "HALF_OPEN":
            logger.info("circuit_breaker_closed")
            self._state = "CLOSED"
            self._failures = 0
            
    def _on_failure(self) -> None:
        self._failures += 1
        self._last_failure_time = time.time()
        
        if self._state == "HALF_OPEN" or self._failures >= self.failure_threshold:
            if self._state != "OPEN":
                logger.warning("circuit_breaker_opened", failures=self._failures)
            self._state = "OPEN"
