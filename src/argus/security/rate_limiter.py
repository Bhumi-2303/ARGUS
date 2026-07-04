"""Rate limiting utility."""
import time
from typing import Dict, Tuple

class TokenBucketRateLimiter:
    """In-memory token bucket rate limiter."""
    def __init__(self):
        self._buckets: Dict[str, Tuple[float, float]] = {} # key -> (tokens, last_refilled)
        
    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, float]:
        """
        Check if a request is allowed.
        Returns: (allowed, remaining_tokens, reset_time_seconds)
        """
        now = time.time()
        
        if key not in self._buckets:
            # First request, start with max_requests - 1
            self._buckets[key] = (float(max_requests - 1), now)
            return True, max_requests - 1, now + window_seconds
            
        tokens, last_refilled = self._buckets[key]
        
        # Calculate how many tokens to add based on elapsed time
        elapsed = now - last_refilled
        refill_rate = max_requests / float(window_seconds)
        new_tokens = min(float(max_requests), tokens + (elapsed * refill_rate))
        
        if new_tokens >= 1.0:
            # Consume 1 token
            new_tokens -= 1.0
            self._buckets[key] = (new_tokens, now)
            # Rough estimate of reset time based on remaining tokens
            reset_time = now + ((max_requests - new_tokens) / refill_rate)
            return True, int(new_tokens), reset_time
        else:
            # Rate limit exceeded
            # Calculate time until 1 token is available
            wait_time = (1.0 - new_tokens) / refill_rate
            self._buckets[key] = (new_tokens, now)
            return False, 0, now + wait_time

rate_limiter = TokenBucketRateLimiter()
