"""MetaAgent konsolidasyon testleri (adım 11)."""

from __future__ import annotations

import pytest

from agents.meta_agent import MetaAgent
from models.reports import DepotRiskReport
from models.risk import RiskLevel, RiskResult


@pytest.fixture(autouse=True)
def _no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def _report(depot_id, *results):
    return DepotRiskReport(depot_id=depot_id, depot_name=depot_id, results=list(results))


def _crit(item_id, score=90):
    return RiskResult(item_id=item_id, depot_id="x", score=score, level=RiskLevel.CRITICAL)


def test_prioritizes_depots_by_critical_then_score():
    reports = [
        _report("dusuk"),  # 0 kritik
        _report("orta", _crit("a", 80)),  # 1 kritik, skor 80
        _report("yuksek", _crit("b", 95), _crit("c", 90)),  # 2 kritik
    ]
    consolidated = MetaAgent().consolidate(reports)
    assert consolidated.prioritized_depots == ["yuksek", "orta", "dusuk"]


def test_executive_summary_uses_template_fallback():
    reports = [_report("ankara", _crit("a"))]
    consolidated = MetaAgent().consolidate(reports)
    assert "Türkiye geneli" in consolidated.executive_summary
    assert "1 kritik" in consolidated.executive_summary


def test_handles_empty_report_list():
    consolidated = MetaAgent().consolidate([])
    assert consolidated.prioritized_depots == []
    assert consolidated.executive_summary
