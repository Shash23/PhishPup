"""
Thin wrapper around core engine; returns API response shape.
If metadata contains user_context_description, interpret it and store in metadata["interpreted_context"].
"""
from core.engine import run_analysis
from schemas.analyze import AnalyzeResponse
from services.context_service import interpret_context


def analyze_text(conversation: str, draft: str, metadata: dict) -> AnalyzeResponse:
    meta = dict(metadata)
    desc = meta.get("user_context_description") or ""
    if desc and isinstance(desc, str) and desc.strip() and "interpreted_context" not in meta:
        interpreted = interpret_context(desc.strip())
        if interpreted:
            meta["interpreted_context"] = interpreted
    result = run_analysis(conversation, draft, meta)
    return AnalyzeResponse(
        action=result.action,
        risk_level=result.risk_level,
        recoverability=result.recoverability,
        pressure_signals=result.pressure_signals,
        explanation=result.explanation,
    )
