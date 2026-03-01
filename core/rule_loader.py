"""
Load and parse behavior_rules.json into engine models.
"""
import json
from pathlib import Path

from core.models import (
    ActionRule,
    DefaultAction,
    ExplanationLines,
    LoadedRules,
    PersuasionRule,
)


def _parse_explanation(data: dict) -> ExplanationLines:
    exp = data.get("explanation") or {}
    if isinstance(exp, dict):
        return ExplanationLines(
            ask_line=exp.get("ask_line", ""),
            tactic_line=exp.get("tactic_line", ""),
            outcome_line=exp.get("outcome_line", ""),
            suggestion_line=exp.get("suggestion_line", ""),
        )
    return ExplanationLines("", "", "", "")


def load_rules(rules_path: Path) -> LoadedRules:
    with open(rules_path, encoding="utf-8") as f:
        raw = json.load(f)

    actions = []
    for a in raw.get("actions", []):
        actions.append(
            ActionRule(
                id=a["id"],
                keywords=[str(k).strip() for k in a.get("keywords", [])],
                recoverability=a.get("recoverability", "CONDITIONAL"),
                label=a.get("label", a["id"]),
                severity=a.get("severity", "medium"),
                explanation=_parse_explanation(a),
            )
        )

    persuasion = []
    for p in raw.get("persuasion", []):
        persuasion.append(
            PersuasionRule(
                id=p["id"],
                keywords=[str(k).strip() for k in p.get("keywords", [])],
                label=p.get("label", p["id"]),
            )
        )

    default = raw.get("default_action", {})
    default_action = DefaultAction(
        id=default.get("id", "UNKNOWN"),
        recoverability=default.get("recoverability", "REVERSIBLE"),
        label=default.get("label", "No specific risky action detected"),
        severity=default.get("severity", "low"),
        explanation=_parse_explanation(default),
    )

    return LoadedRules(
        actions=actions,
        persuasion=persuasion,
        default_action=default_action,
    )
