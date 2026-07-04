"""Prompt injection detection."""
import re
from typing import List, Tuple
from argus.core.exceptions import InjectionDetectedError

# Common prompt injection patterns
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous\s+)?instructions",
    r"(?i)you\s+are\s+now",
    r"(?i)disregard\s+(the\s+)?above",
    r"(?i)instead\s+do\s+this",
    r"(?i)forget\s+(about\s+)?what\s+i\s+told\s+you",
    r"(?i)system\s+prompt"
]

def detect_injection(text: str) -> Tuple[bool, float, List[str]]:
    """
    Detect if text contains prompt injection attempts.
    Returns (is_injection, confidence_score, matched_patterns).
    """
    if not text:
        return False, 0.0, []
        
    matches = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            matches.append(pattern)
            
    if not matches:
        return False, 0.0, []
        
    # Calculate confidence based on number of matches (simple heuristic)
    confidence = min(1.0, len(matches) * 0.3)
    return True, confidence, matches
