"""
Data models for the analysis engine.
Rule structures and engine result; no business logic here.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExplanationLines:
    ask_line: str
    tactic_line: str
    outcome_line: str
    suggestion_line: str


@dataclass
class ActionRule:
    id: str
    keywords: List[str]
    recoverability: str
    label: str
    severity: str  # "high" | "medium" | "low"
    explanation: ExplanationLines


@dataclass
class PersuasionRule:
    id: str
    keywords: List[str]
    label: str


@dataclass
class DefaultAction:
    id: str
    recoverability: str
    label: str
    severity: str
    explanation: ExplanationLines


@dataclass
class LoadedRules:
    actions: List[ActionRule]
    persuasion: List[PersuasionRule]
    default_action: DefaultAction


@dataclass
class EngineResult:
    action: str
    risk_level: str  # LOW | MEDIUM | HIGH
    recoverability: str
    pressure_signals: List[str] = field(default_factory=list)
    explanation: str = ""
