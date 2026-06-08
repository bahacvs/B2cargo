"""StockRiskAgent birim testleri (deterministik, sıfır AI).

Gerçek config/risk_weights.yaml ile çalışır: eşikler 75/45/25; depo sapması
base45+per_degree10 (max100), araç base40+per_degree6 (max70), expiry_passed 80,
expiry_imminent 30, shipment_delay 25, low_stock 15.
"""

from __future__ import annotations

from datetime import date, timedelta

from agents.sub_agents.stock_risk import StockRiskAgent
from models.risk import RiskLevel
from models.signals import (
    DeviationDirection,
    DeviationSource,
    TemperatureDeviation,
)
from models.stock import DepotSnapshot, StockItem

TODAY = date(2026, 6, 8)


def _snapshot(*items: StockItem) -> DepotSnapshot:
    return DepotSnapshot(depot_id="ankara", items=list(items))


def _item(**kw) -> StockItem:
    base = {"item_id": "i1", "name": "X", "depot_id": "ankara", "quantity": 100}
    base.update(kw)
    return StockItem(**base)


def _dev(source: DeviationSource, magnitude: float, item_id: str = "i1") -> TemperatureDeviation:
    return TemperatureDeviation(
        item_id=item_id,
        depot_id="ankara",
        source=source,
        direction=DeviationDirection.ABOVE_MAX,
        measured_c=0.0,
        limit_c=0.0,
        magnitude_c=magnitude,
    )


def _result_for(results, item_id):
    return next(r for r in results if r.item_id == item_id)


def test_frozen_depot_deviation_is_critical():
    item = _item(temp_min_c=-18, temp_max_c=-15, zone_id="frozen")
    dev = _dev(DeviationSource.DEPOT_ZONE, magnitude=5)  # 45 + 10*5 = 95
    res = StockRiskAgent().assess(_snapshot(item), deviations=[dev], today=TODAY)
    r = _result_for(res, "i1")
    assert r.score == 95
    assert r.level is RiskLevel.CRITICAL


def test_vehicle_deviation_plus_delay_is_critical_with_two_reasons():
    item = _item(temp_min_c=2, temp_max_c=8, vehicle_id="v1", shipment_id="s1")
    dev = _dev(DeviationSource.VEHICLE, magnitude=6)  # min(40+36, 70) = 70
    res = StockRiskAgent().assess(
        _snapshot(item), deviations=[dev], delayed_shipments={"s1"}, today=TODAY
    )
    r = _result_for(res, "i1")
    codes = {reason.code for reason in r.reasons}
    assert codes == {"temp_deviation_vehicle", "shipment_delay"}
    assert r.score == 95  # 70 + 25
    assert r.level is RiskLevel.CRITICAL


def test_dry_goods_no_temp_but_low_stock_reason_runs():
    item = _item(item_id="dry", quantity=3)  # temp null → izleme yok
    res = StockRiskAgent().assess(_snapshot(item), today=TODAY)
    r = _result_for(res, "dry")
    assert [reason.code for reason in r.reasons] == ["low_stock"]
    assert r.score == 15
    assert r.level is RiskLevel.LOW


def test_expiry_passed_is_critical():
    item = _item(expiry_date=TODAY - timedelta(days=1))
    res = StockRiskAgent().assess(_snapshot(item), today=TODAY)
    r = _result_for(res, "i1")
    assert r.reasons[0].code == "expiry_passed"
    assert r.score == 80
    assert r.level is RiskLevel.CRITICAL


def test_expiry_imminent_is_medium():
    item = _item(expiry_date=TODAY + timedelta(days=2))
    res = StockRiskAgent().assess(_snapshot(item), today=TODAY)
    r = _result_for(res, "i1")
    assert r.reasons[0].code == "expiry_imminent"
    assert r.score == 30
    assert r.level is RiskLevel.MEDIUM


def test_expiry_far_no_reason():
    item = _item(expiry_date=TODAY + timedelta(days=30))
    res = StockRiskAgent().assess(_snapshot(item), today=TODAY)
    assert _result_for(res, "i1").reasons == []


def test_normal_item_is_low_with_zero_score():
    item = _item(quantity=500)
    res = StockRiskAgent().assess(_snapshot(item), today=TODAY)
    r = _result_for(res, "i1")
    assert r.score == 0
    assert r.level is RiskLevel.LOW


def test_depot_deviation_points_capped_at_max():
    item = _item(temp_min_c=-18, temp_max_c=-15, zone_id="frozen")
    dev = _dev(DeviationSource.DEPOT_ZONE, magnitude=20)  # 45+200 → cap 100
    res = StockRiskAgent().assess(_snapshot(item), deviations=[dev], today=TODAY)
    assert _result_for(res, "i1").score == 100


def test_delay_only_is_medium():
    item = _item(shipment_id="s9")
    res = StockRiskAgent().assess(
        _snapshot(item), delayed_shipments={"s9"}, today=TODAY
    )
    r = _result_for(res, "i1")
    assert r.score == 25
    assert r.level is RiskLevel.MEDIUM


def test_low_stock_boundary_inclusive():
    item = _item(quantity=5)  # min_quantity = 5, <= → tetiklenir
    res = StockRiskAgent().assess(_snapshot(item), today=TODAY)
    assert _result_for(res, "i1").reasons[0].code == "low_stock"


def test_thresholds_are_config_driven_not_hardcoded():
    # Aynı skor (30), farklı eşiklerle farklı seviye → kod değişmeden davranış değişir.
    weights = {
        "thresholds": {"critical": 20, "high": 10, "medium": 5},
        "reasons": {
            "shipment_delay": {"points": 30, "description": "gecikme"},
            "low_stock": {"points": 0, "min_quantity": 0},
            "expiry_imminent": {"points": 0, "within_days": 0},
            "expiry_passed": {"points": 0},
            "temp_deviation_depot": {"base": 0, "per_degree": 0, "max": 0},
            "temp_deviation_vehicle": {"base": 0, "per_degree": 0, "max": 0},
        },
    }
    item = _item(shipment_id="s1")
    res = StockRiskAgent(weights=weights).assess(
        _snapshot(item), delayed_shipments={"s1"}, today=TODAY
    )
    # 30 puan, kritik eşiği 20 → CRITICAL (varsayılan yaml'da 30 sadece ORTA olurdu)
    assert _result_for(res, "i1").level is RiskLevel.CRITICAL
