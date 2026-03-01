"""
Optional AI context interpreter. Converts a human description into structured context.
If OPENAI_API_KEY is not set or the call fails, returns DEFAULT_CONTEXT so the UI always shows a valid box.
In-memory cache avoids repeated OpenAI calls for the same description.
"""
import json
import os
from typing import Any, Dict

DEFAULT_CONTEXT = {
    "category": "general",
    "sensitivity": "low",
    "focus_checks": [],
}

_CONTEXT_CACHE: Dict[str, Dict[str, Any]] = {}

SYSTEM_PROMPT = """You convert a human description of a communication situation into structured verification context.

Return STRICT JSON ONLY:

{
"category": string,
"sensitivity": "low" | "medium" | "high",
"focus_checks": string[]
}

No explanations. No extra text.

If unclear, return:
{ "category": "general", "sensitivity": "low", "focus_checks": [] }
"""


def normalize_context(data: dict) -> dict:
    """Ensure a valid context object for the UI. Prevents random model formats from breaking the demo."""
    if not isinstance(data, dict):
        return DEFAULT_CONTEXT.copy()

    category = str(data.get("category", "general"))
    sensitivity = data.get("sensitivity", "low")
    if sensitivity not in ("low", "medium", "high"):
        sensitivity = "low"

    focus = data.get("focus_checks", [])
    if not isinstance(focus, list):
        focus = []

    return {
        "category": category,
        "sensitivity": sensitivity,
        "focus_checks": focus,
    }


def interpret_context(description: str) -> Dict[str, Any]:
    """
    If description empty: return {}.
    Cache hit: return cached normalized result.
    If no API key or on failure: return DEFAULT_CONTEXT so the UI always shows a context box.
    """
    if not description or not description.strip():
        return {}
    key = description.strip()
    if key in _CONTEXT_CACHE:
        return _CONTEXT_CACHE[key]

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        result = DEFAULT_CONTEXT.copy()
        _CONTEXT_CACHE[key] = result
        return result
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": key},
            ],
            temperature=0,
        )
        content = (resp.choices[0].message.content or "").strip()
        if not content:
            result = DEFAULT_CONTEXT.copy()
            _CONTEXT_CACHE[key] = result
            return result
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            )
        data = json.loads(content)
        result = normalize_context(data)
        _CONTEXT_CACHE[key] = result
        return result
    except Exception:
        result = DEFAULT_CONTEXT.copy()
        _CONTEXT_CACHE[key] = result
        return result
