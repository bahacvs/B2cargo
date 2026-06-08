"""ExplanationAgent / TemplateExplanation testleri (adım 7)."""

from __future__ import annotations

import pytest

from agents.llm import LLMUnavailable
from agents.sub_agents.explanation import ExplanationAgent, TemplateExplanation
from models.risk import RiskLevel, RiskReason, RiskResult


def _result(item_id, score, level, codes):
    r = RiskResult(item_id=item_id, depot_id="ankara", score=score, level=level)
    r.reasons = [RiskReason(code=c, description="", points=score) for c in codes]
    return r


def test_template_all_normal():
    text = TemplateExplanation().generate("Ankara Depo", [])
    assert "tamamı normal" in text


def test_template_lists_critical_items():
    results = [
        _result("a", 95, RiskLevel.CRITICAL, ["temp_deviation_depot"]),
        _result("b", 10, RiskLevel.LOW, []),
    ]
    text = TemplateExplanation().generate("Ankara Depo", results)
    assert "1 kritik" in text
    assert "a" in text
    assert "temp_deviation_depot" in text
    assert "b" not in text  # LOW kalem listelenmez


def test_explanation_agent_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMUnavailable):
        ExplanationAgent().generate("Ankara Depo", [])
