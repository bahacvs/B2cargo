"""StockRiskAgent — deterministik, sıfır AI.

Kalem başına risk skorunu `config/risk_weights.yaml`'daki ağırlıklardan üretir.
Hiçbir eşik kodda gömülü değildir; yaml değişince sonuç değişir, kod değişmez.
Sıcaklık sapma sinyalleri TemperatureMonitorAgent'tan gelir.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from datetime import date

from config import load_risk_weights
from models.risk import RiskReason, RiskResult
from models.signals import DeviationSource, TemperatureDeviation
from models.stock import DepotSnapshot, StockItem

_SOURCE_TO_REASON = {
    DeviationSource.DEPOT_ZONE: "temp_deviation_depot",
    DeviationSource.VEHICLE: "temp_deviation_vehicle",
}


class StockRiskAgent:
    """Kalem bazlı deterministik risk skorlayıcı."""

    def __init__(self, weights: dict | None = None) -> None:
        self._weights = weights or load_risk_weights()
        self._thresholds = self._weights["thresholds"]
        self._reasons_cfg = self._weights["reasons"]

    def assess(
        self,
        snapshot: DepotSnapshot,
        deviations: Iterable[TemperatureDeviation] | None = None,
        delayed_shipments: Iterable[str] | None = None,
        today: date | None = None,
    ) -> list[RiskResult]:
        today = today or date.today()
        delayed = set(delayed_shipments or [])

        dev_by_item: dict[str, list[TemperatureDeviation]] = defaultdict(list)
        for dev in deviations or []:
            dev_by_item[dev.item_id].append(dev)

        results: list[RiskResult] = []
        for item in snapshot.items:
            result = RiskResult(item_id=item.item_id, depot_id=item.depot_id)
            for reason in self._reasons_for(
                item, dev_by_item.get(item.item_id, []), delayed, today
            ):
                result.reasons.append(reason)
            result.recompute(self._thresholds)
            results.append(result)
        return results

    # --- gerekçe üreticileri -------------------------------------------------

    def _reasons_for(
        self,
        item: StockItem,
        deviations: list[TemperatureDeviation],
        delayed: set[str],
        today: date,
    ) -> list[RiskReason]:
        reasons: list[RiskReason] = []

        for dev in deviations:
            reasons.append(self._temp_reason(dev))

        expiry_reason = self._expiry_reason(item, today)
        if expiry_reason:
            reasons.append(expiry_reason)

        if item.shipment_id and item.shipment_id in delayed:
            reasons.append(self._flat_reason("shipment_delay"))

        if self._is_low_stock(item):
            reasons.append(self._flat_reason("low_stock"))

        return reasons

    def _temp_reason(self, dev: TemperatureDeviation) -> RiskReason:
        code = _SOURCE_TO_REASON[dev.source]
        cfg = self._reasons_cfg[code]
        points = min(cfg["base"] + cfg["per_degree"] * dev.magnitude_c, cfg["max"])
        return RiskReason(
            code=code,
            description=f"{cfg['description']} ({dev.measured_c}°C, sapma {dev.magnitude_c}°C)",
            weight=cfg["base"],
            points=round(points, 4),
        )

    def _expiry_reason(self, item: StockItem, today: date) -> RiskReason | None:
        if item.expiry_date is None:
            return None
        if item.expiry_date < today:
            return self._flat_reason("expiry_passed")
        cfg = self._reasons_cfg["expiry_imminent"]
        if (item.expiry_date - today).days <= cfg["within_days"]:
            return self._flat_reason("expiry_imminent")
        return None

    def _is_low_stock(self, item: StockItem) -> bool:
        cfg = self._reasons_cfg["low_stock"]
        return item.quantity <= cfg["min_quantity"]

    def _flat_reason(self, code: str) -> RiskReason:
        cfg = self._reasons_cfg[code]
        return RiskReason(
            code=code,
            description=cfg["description"],
            weight=cfg["points"],
            points=cfg["points"],
        )
