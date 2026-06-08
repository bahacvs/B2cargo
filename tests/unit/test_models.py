"""Model birim testleri: sıcaklık izleme kapısı, risk seviyesi eşikleri, RiskResult."""

from __future__ import annotations

import pytest

from models.risk import RiskLevel, RiskReason, RiskResult
from models.stock import StockItem, needs_temp_monitoring


def _item(**kw) -> StockItem:
    base = {"item_id": "i1", "name": "X", "depot_id": "ankara"}
    base.update(kw)
    return StockItem(**base)


def test_needs_temp_monitoring_true_when_both_bounds_set():
    assert needs_temp_monitoring(_item(temp_min_c=-18, temp_max_c=-15)) is True


@pytest.mark.parametrize(
    "tmin,tmax",
    [(None, None), (-18, None), (None, -15)],
)
def test_needs_temp_monitoring_false_when_any_bound_null(tmin, tmax):
    assert needs_temp_monitoring(_item(temp_min_c=tmin, temp_max_c=tmax)) is False


@pytest.mark.parametrize(
    "score,expected",
    [
        (0, RiskLevel.LOW),
        (24, RiskLevel.LOW),
        (25, RiskLevel.MEDIUM),
        (44, RiskLevel.MEDIUM),
        (45, RiskLevel.HIGH),
        (74, RiskLevel.HIGH),
        (75, RiskLevel.CRITICAL),
        (100, RiskLevel.CRITICAL),
    ],
)
def test_risk_level_from_score_boundaries(score, expected):
    assert RiskLevel.from_score(score) is expected


def test_risk_level_respects_custom_thresholds():
    thresholds = {"critical": 50, "high": 30, "medium": 10}
    assert RiskLevel.from_score(50, thresholds) is RiskLevel.CRITICAL
    assert RiskLevel.from_score(49, thresholds) is RiskLevel.HIGH


def test_risk_result_add_reason_recomputes_score_and_level():
    r = RiskResult(item_id="i1", depot_id="ankara")
    r.add_reason(RiskReason(code="a", description="", points=40))
    r.add_reason(RiskReason(code="b", description="", points=40))
    assert r.score == 80
    assert r.level is RiskLevel.CRITICAL


def test_risk_result_recompute_with_custom_thresholds():
    r = RiskResult(item_id="i1", depot_id="ankara")
    r.reasons.append(RiskReason(code="a", description="", points=12))
    r.recompute({"critical": 50, "high": 30, "medium": 10})
    assert r.score == 12
    assert r.level is RiskLevel.MEDIUM
