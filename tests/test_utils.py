"""
Test helper: run analysis via core engine only. No HTTP, no FastAPI.
"""
from typing import Optional

from core.engine import run_analysis


def run_case(
    conversation: str = "",
    draft: str = "",
    context_category: Optional[str] = None,
) -> dict:
    """
    Call core.engine.run_analysis with the given inputs.
    Returns the EngineResult as a dict (action, risk_level, recoverability, pressure_signals, explanation).
    """
    metadata = {}
    if context_category:
        metadata["interpreted_context"] = {
            "category": context_category,
            "sensitivity": "medium",
            "focus_checks": [],
        }
    result = run_analysis(conversation=conversation, draft=draft, metadata=metadata)
    return {
        "action": result.action,
        "risk_level": result.risk_level,
        "recoverability": result.recoverability,
        "pressure_signals": list(result.pressure_signals),
        "explanation": result.explanation,
    }
