"""
Pydantic schemas for POST /analyze request and response.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class ActionEnum(str, Enum):
    SEND_MONEY = "SEND_MONEY"
    SHARE_CODE = "SHARE_CODE"
    GRANT_ACCESS = "GRANT_ACCESS"
    CLICK_LINK = "CLICK_LINK"
    DOWNLOAD = "DOWNLOAD"
    UNKNOWN = "UNKNOWN"


class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecoverabilityEnum(str, Enum):
    REVERSIBLE = "REVERSIBLE"
    CONDITIONAL = "CONDITIONAL"
    IRREVERSIBLE = "IRREVERSIBLE"


class AnalyzeRequest(BaseModel):
    """Supports legacy { text } and new { conversation, draft, metadata }."""
    text: Optional[str] = Field(None, description="Legacy: message to analyze (used as draft if draft missing)")
    conversation: Optional[str] = Field(None, description="Conversation context")
    draft: Optional[str] = Field(None, description="Draft message to analyze")
    metadata: Optional[Dict[str, Any]] = Field(None, description="e.g. recipients, source")

    def normalized(self) -> Tuple[str, str, Dict[str, Any]]:
        """Returns (conversation, draft, metadata). Backwards-compat: if only text provided, treat as draft."""
        draft_val = self.draft if self.draft is not None else (self.text or "")
        conversation_val = self.conversation if self.conversation is not None else ""
        metadata_val = self.metadata if self.metadata is not None else {}
        return (conversation_val, draft_val, metadata_val)


class InterpretContextRequest(BaseModel):
    description: str = Field("", description="Human description of the communication situation")


class AnalyzeResponse(BaseModel):
    action: str = Field(..., description="Detected action type")
    risk_level: str = Field(..., description="LOW | MEDIUM | HIGH")
    recoverability: str = Field(..., description="REVERSIBLE | CONDITIONAL | IRREVERSIBLE")
    pressure_signals: List[str] = Field(default_factory=list, description="List of persuasion signals")
    explanation: str = Field(..., description="Human-readable explanation")
