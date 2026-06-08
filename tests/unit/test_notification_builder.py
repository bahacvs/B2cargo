"""NotificationBuilder testleri (adım 9)."""

from __future__ import annotations

from agents.sub_agents.notification_builder import NotificationBuilder
from models.reports import DepotRiskReport
from models.risk import RiskLevel, RiskResult

RULES = {
    "channels": {
        "CRITICAL": ["whatsapp", "email"],
        "HIGH": ["email"],
        "MEDIUM": ["dashboard"],
        "LOW": [],
    },
    "throttle": {"max_per_run": 50},
}


def _report(*results):
    return DepotRiskReport(depot_id="ankara", results=list(results))


def _result(item_id, level):
    return RiskResult(item_id=item_id, depot_id="ankara", score=80, level=level)


def test_low_level_produces_no_payload():
    report = _report(_result("a", RiskLevel.LOW))
    assert NotificationBuilder(RULES).build(report) == []


def test_one_payload_per_channel_for_level():
    report = _report(_result("crit", RiskLevel.CRITICAL))
    payloads = NotificationBuilder(RULES).build(report)
    channels = {p["channel"] for p in payloads}
    assert channels == {"whatsapp", "email"}


def test_sorted_by_score_descending():
    r_low = RiskResult(item_id="b", depot_id="ankara", score=46, level=RiskLevel.HIGH)
    r_high = RiskResult(item_id="a", depot_id="ankara", score=90, level=RiskLevel.CRITICAL)
    payloads = NotificationBuilder(RULES).build(_report(r_low, r_high))
    assert payloads[0]["item_id"] == "a"  # en yüksek skor önce


def test_max_per_run_cap():
    rules = {**RULES, "throttle": {"max_per_run": 1}}
    report = _report(_result("a", RiskLevel.CRITICAL))
    assert len(NotificationBuilder(rules).build(report)) == 1
