"""
Deterministic behavioral analysis engine.
Token-based matching; no ML, no external APIs.
Context (metadata, conversation) is used to add virtual tokens before rule matching.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from core.models import (
    ActionRule,
    DefaultAction,
    EngineResult,
    LoadedRules,
    PersuasionRule,
)
from core.rule_loader import load_rules

_SEVERITY_ORDER = {"high": 2, "medium": 1, "low": 0}

# Categories that imply account/security verification (case-insensitive)
_VERIFICATION_CATEGORIES = {"account verification", "security verification", "login verification"}

# Categories that imply payment/transfer
_PAYMENT_CATEGORIES = {"payment", "transfer", "money transfer", "wire transfer", "send money", "pay"}

# Categories that imply scheduling/commitment
_COMMITMENT_CATEGORIES = {"scheduling", "meeting", "commitment", "appointment", "calendar"}

# Commitment phrases in draft (token sequences)
_COMMITMENT_PHRASES = ["i will", "i'll", "definitely", "see you then", "be there"]

# Conversation words that imply urgency (feed into persuasion)
_URGENCY_WORDS = {"urgent", "immediately", "asap", "right now", "locked", "suspended"}

# Conversation words that imply authority (feed into persuasion)
_AUTHORITY_WORDS = {"it support", "administrator", "bank", "manager", "security team", "boss", "ceo", "hr", "official"}


def _normalize(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.strip().split()).lower()


def _tokenize(normalized: str) -> List[str]:
    if not normalized:
        return []
    return normalized.split()


def _phrase_tokens(phrase: str) -> List[str]:
    return _normalize(phrase).split()


def _phrase_matches(tokens: List[str], phrase: str) -> bool:
    phrase_tok = _phrase_tokens(phrase)
    if not phrase_tok:
        return False
    for i in range(len(tokens) - len(phrase_tok) + 1):
        if tokens[i : i + len(phrase_tok)] == phrase_tok:
            return True
    return False


def _count_matching_keywords(tokens: List[str], keywords: List[str]) -> int:
    count = 0
    for phrase in keywords:
        if _phrase_matches(tokens, phrase):
            count += 1
    return count


def _select_action(tokens: List[str], rules: LoadedRules) -> Tuple[Union[ActionRule, DefaultAction], int]:
    candidates = []
    for idx, action in enumerate(rules.actions):
        count = _count_matching_keywords(tokens, action.keywords)
        if count > 0:
            candidates.append((count, _SEVERITY_ORDER.get(action.severity, 0), idx, action))
    if not candidates:
        return rules.default_action, 0
    # Sort: highest count, then higher severity, then earlier in list (lower idx)
    candidates.sort(key=lambda x: (-x[0], -x[1], x[2]))
    best = candidates[0]
    return best[3], best[0]


def _detect_persuasion(tokens: List[str], rules: LoadedRules) -> List[str]:
    result = []
    for p in rules.persuasion:
        if _count_matching_keywords(tokens, p.keywords) > 0:
            result.append(p.id)
    return result


def _compute_risk_level(
    action_id: str,
    action_severity: str,
    recoverability: str,
    pressure_signals: List[str],
) -> str:
    pressure_count = len(pressure_signals)
    has_urgency = "urgency" in pressure_signals
    has_authority = "authority" in pressure_signals

    if action_id == "UNKNOWN":
        return "LOW"

    base = "LOW"
    if action_severity == "high":
        base = "HIGH"
    elif action_severity == "medium":
        base = "MEDIUM"

    level_val = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}[base]

    if recoverability == "IRREVERSIBLE" and level_val < 1:
        level_val = 1
    if recoverability == "REVERSIBLE" and level_val > 1:
        level_val = 1

    if action_id in ("SEND_MONEY", "SHARE_CODE") and pressure_count >= 1:
        level_val = 2
    if action_id == "GRANT_ACCESS" and (has_urgency or has_authority):
        level_val = 2
    if pressure_count >= 2:
        level_val = min(2, level_val + 1)

    if recoverability == "REVERSIBLE" and level_val > 1:
        level_val = 1
    if recoverability == "IRREVERSIBLE" and level_val < 1:
        level_val = 1

    return ["LOW", "MEDIUM", "HIGH"][level_val]


def _build_explanation(action, pressure_labels: List[str]) -> str:
    exp = action.explanation
    parts = [
        exp.ask_line,
        exp.tactic_line,
        exp.outcome_line,
        exp.suggestion_line,
    ]
    pressure_list = ", ".join(pressure_labels) if pressure_labels else "none"
    return "\n\n".join(parts).replace("{pressure_list}", pressure_list)


def _category_matches(category: str, allowed: set) -> bool:
    if not category or not isinstance(category, str):
        return False
    return category.strip().lower() in allowed


def _draft_has_4_to_8_digits(text: str) -> bool:
    return bool(re.search(r"\b\d{4,8}\b", text))


def _draft_has_currency_or_large_number(text: str) -> bool:
    if re.search(r"[$€£¥₹]|\b\d{3,}\b", text):
        return True
    return False


def _draft_has_commitment_phrase(normalized_draft: str) -> bool:
    for phrase in _COMMITMENT_PHRASES:
        if phrase in normalized_draft:
            return True
    return False


def _conversation_has_urgency(conversation: str) -> bool:
    if not conversation:
        return False
    low = _normalize(conversation)
    for w in _URGENCY_WORDS:
        if w in low:
            return True
    return False


def _conversation_has_authority(conversation: str) -> bool:
    if not conversation:
        return False
    low = _normalize(conversation)
    for w in _AUTHORITY_WORDS:
        if w in low:
            return True
    return False


def infer_contextual_tokens(
    text_tokens: List[str],
    metadata: Optional[Dict[str, Any]] = None,
    conversation: Optional[str] = None,
    normalized_draft: str = "",
) -> List[str]:
    """
    Add virtual tokens from context before rule matching.
    Returns list of extra tokens to append to the draft token list.
    """
    extra: List[str] = []
    meta = metadata or {}
    interpreted = meta.get("interpreted_context") or {}
    if not isinstance(interpreted, dict):
        interpreted = {}
    category = (interpreted.get("category") or "").strip().lower()
    conv = (conversation or "").strip()
    draft_text = normalized_draft or " ".join(text_tokens)

    # ACCOUNT VERIFICATION: category + 4-8 digit number in draft
    if _category_matches(category, _VERIFICATION_CATEGORIES) and _draft_has_4_to_8_digits(draft_text):
        extra.append("verification")
        extra.append("code")

    # MONEY / PAYMENT: category indicates payment + currency or multi-digit number
    if category and any(p in category for p in _PAYMENT_CATEGORIES):
        if _draft_has_currency_or_large_number(draft_text):
            extra.append("transfer")

    # COMMITMENT: category indicates scheduling + commitment phrases in draft
    if category and any(c in category for c in _COMMITMENT_CATEGORIES):
        if _draft_has_commitment_phrase(normalized_draft or draft_text):
            extra.append("commitment_confirmation")

    # Conversation pressure: add tokens that match existing persuasion keywords
    if _conversation_has_urgency(conv):
        extra.append("urgent")
    if _conversation_has_authority(conv):
        extra.append("manager")

    return extra


def analyze(
    text: str,
    rules: LoadedRules,
    metadata: Optional[Dict[str, Any]] = None,
    conversation: Optional[str] = None,
) -> EngineResult:
    normalized = _normalize(text)
    tokens = _tokenize(normalized)
    virtual = infer_contextual_tokens(tokens, metadata, conversation, normalized)
    tokens = tokens + virtual

    selected_action, _ = _select_action(tokens, rules)
    pressure_ids = _detect_persuasion(tokens, rules)

    if isinstance(selected_action, DefaultAction):
        action_id = selected_action.id
        recoverability = selected_action.recoverability
        severity = selected_action.severity
    else:
        action_id = selected_action.id
        recoverability = selected_action.recoverability
        severity = selected_action.severity

    risk_level = _compute_risk_level(action_id, severity, recoverability, pressure_ids)

    id_to_label = {p.id: p.label for p in rules.persuasion}
    pressure_labels = [id_to_label.get(pid, pid) for pid in pressure_ids]
    explanation = _build_explanation(selected_action, pressure_labels)

    return EngineResult(
        action=action_id,
        risk_level=risk_level,
        recoverability=recoverability,
        pressure_signals=pressure_ids,
        explanation=explanation,
    )


def get_default_rules_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "behavior_rules.json"


def run_analysis(
    conversation: str,
    draft: str,
    metadata: dict,
    rules_path: Union[Path, None] = None,
) -> EngineResult:
    """Entry point for API/embed. Draft + context (metadata, conversation) are used for analysis."""
    path = rules_path or get_default_rules_path()
    rules = load_rules(path)
    return analyze(draft, rules, metadata=metadata, conversation=conversation or None)


def _cli():
    import sys
    path = get_default_rules_path()
    rules = load_rules(path)
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "send me the verification code"
    result = analyze(message, rules, metadata=None, conversation=None)
    print("Input:", repr(message))
    print("Action:", result.action)
    print("Risk level:", result.risk_level)
    print("Recoverability:", result.recoverability)
    print("Pressure signals:", result.pressure_signals)
    print("Explanation:")
    print(result.explanation)


if __name__ == "__main__":
    _cli()
