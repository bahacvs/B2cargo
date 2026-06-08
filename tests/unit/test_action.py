"""ActionAgent testleri (adım 8)."""

from __future__ import annotations

from agents.sub_agents.action import ActionAgent
from models.risk import RiskLevel, RiskReason, RiskResult


def _result(item_id, level, codes):
    r = RiskResult(item_id=item_id, depot_id="ankara", score=50, level=level)
    r.reasons = [RiskReason(code=c, description="", points=10) for c in codes]
    return r


def test_low_items_excluded():
    results = [_result("a", RiskLevel.LOW, ["low_stock"])]
    assert ActionAgent().recommend("Ankara", results) == []


def test_actions_mapped_from_reason_codes():
    results = [_result("a", RiskLevel.CRITICAL, ["temp_deviation_depot", "expiry_passed"])]
    recs = ActionAgent().recommend("Ankara", results)
    assert len(recs) == 1
    actions = recs[0]["actions"]
    assert any("soğutma" in a for a in actions)
    assert any("imha" in a for a in actions)


def test_recommendations_sorted_by_priority():
    results = [
        _result("med", RiskLevel.MEDIUM, ["low_stock"]),
        _result("crit", RiskLevel.CRITICAL, ["expiry_passed"]),
        _result("high", RiskLevel.HIGH, ["shipment_delay"]),
    ]
    recs = ActionAgent().recommend("Ankara", results)
    assert [r["item_id"] for r in recs] == ["crit", "high", "med"]


def test_no_claude_note_without_client():
    results = [_result("a", RiskLevel.CRITICAL, ["low_stock"])]
    recs = ActionAgent(client=None).recommend("Ankara", results)
    assert "note" not in recs[0]
