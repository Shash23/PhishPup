"""
API route definitions.
"""
from fastapi import APIRouter

from schemas.analyze import AnalyzeRequest, AnalyzeResponse, InterpretContextRequest
from services.analyze_service import analyze_text
from services.context_service import interpret_context

router = APIRouter()


@router.post("/interpret_context")
def post_interpret_context(request: InterpretContextRequest) -> dict:
    """Optional AI context. Returns {} if no API key or on failure."""
    return interpret_context(request.description or "")


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    conversation, draft, metadata = request.normalized()
    return analyze_text(conversation, draft, metadata)
