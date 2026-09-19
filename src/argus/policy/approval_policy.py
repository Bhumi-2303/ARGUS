def requires_approval(action: str, criticality: int) -> bool:
    """Determine if human approval is required before execution."""
    # Critical rule: High impact actions require human approval safely.
    if action in ["ISOLATE", "ESCALATE"]:
        return True
    return False
