"""
Regression tests: previously safe phrases must never escalate.
All must remain LOW risk.
"""
import pytest

from tests.test_utils import run_case


@pytest.mark.parametrize("draft", [
    "I got your email",
    "Sounds good",
    "Here is the document attached",
    "Hello!",
])
def test_safe_phrases_stay_low(draft):
    result = run_case(draft=draft)
    assert result["risk_level"] == "LOW", (
        f"Draft {draft!r}: expected risk_level LOW, got {result['risk_level']}"
    )
