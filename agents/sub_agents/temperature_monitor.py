"""TemperatureMonitorAgent — saf kural, sıfır AI.

İki sıcaklık boyutunu izler ve sapma sinyali üretir:
  - Depo zonu (Sensor) → DepotZoneTemperature
  - Araç içi (Arvento) → VehicleTemperatureReading

Çıktı StockRiskAgent'ın tüketeceği `TemperatureDeviation` listesi + veri eksikliğinde
`DataQualityAlert` (pipeline durmaz). Sıcaklık izleme kapısı tek otorite:
`needs_temp_monitoring` (models/stock.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from models.signals import (
    DataQualityAlert,
    DeviationDirection,
    DeviationSource,
    TemperatureDeviation,
)
from models.stock import DepotSnapshot, needs_temp_monitoring
from models.temperature import DepotZoneTemperature, VehicleTemperatureReading


@dataclass
class TemperatureMonitorResult:
    deviations: list[TemperatureDeviation] = field(default_factory=list)
    alerts: list[DataQualityAlert] = field(default_factory=list)


class TemperatureMonitorAgent:
    """Sıcaklık sapmalarını deterministik kurallarla tespit eder."""

    def run(
        self,
        snapshot: DepotSnapshot,
        depot_temps: list[DepotZoneTemperature] | None = None,
        vehicle_temps: list[VehicleTemperatureReading] | None = None,
    ) -> TemperatureMonitorResult:
        zone_index = self._latest_by_zone(depot_temps or [])
        vehicle_index = self._latest_by_vehicle(vehicle_temps or [])

        result = TemperatureMonitorResult()

        for item in snapshot.items:
            # Sıcaklık izleme gerektirmeyen kalemler (kuru gıda vb.) atlanır.
            if not needs_temp_monitoring(item):
                continue

            monitored = False

            # 1) Depo zonu sıcaklığı
            if item.zone_id is not None and item.zone_id in zone_index:
                monitored = True
                reading = zone_index[item.zone_id]
                dev = self._check(
                    item_id=item.item_id,
                    depot_id=item.depot_id,
                    measured_c=reading.temp_c,
                    temp_min=item.temp_min_c,
                    temp_max=item.temp_max_c,
                    source=DeviationSource.DEPOT_ZONE,
                )
                if dev:
                    result.deviations.append(dev)

            # 2) Araç içi sıcaklık (yoldaki kalemler)
            if item.vehicle_id is not None and item.vehicle_id in vehicle_index:
                monitored = True
                reading = vehicle_index[item.vehicle_id]
                dev = self._check(
                    item_id=item.item_id,
                    depot_id=item.depot_id,
                    measured_c=reading.temp_c,
                    temp_min=item.temp_min_c,
                    temp_max=item.temp_max_c,
                    source=DeviationSource.VEHICLE,
                )
                if dev:
                    result.deviations.append(dev)

            # 3) İzlenmesi gereken ama ölçümü olmayan kalem → veri kalitesi uyarısı.
            if not monitored:
                result.alerts.append(
                    DataQualityAlert(
                        depot_id=item.depot_id,
                        item_id=item.item_id,
                        code="NO_TEMPERATURE_DATA",
                        message=(
                            "Kalem sıcaklık izlemesi gerektiriyor ancak zon/araç "
                            "ölçümü bulunamadı."
                        ),
                        context={"zone_id": item.zone_id, "vehicle_id": item.vehicle_id},
                    )
                )

        return result

    @staticmethod
    def _check(
        *,
        item_id: str,
        depot_id: str,
        measured_c: float,
        temp_min: float,
        temp_max: float,
        source: DeviationSource,
    ) -> TemperatureDeviation | None:
        """Ölçüm aralık dışındaysa sapma, içindeyse None döner."""

        if measured_c < temp_min:
            return TemperatureDeviation(
                item_id=item_id,
                depot_id=depot_id,
                source=source,
                direction=DeviationDirection.BELOW_MIN,
                measured_c=measured_c,
                limit_c=temp_min,
                magnitude_c=round(temp_min - measured_c, 4),
            )
        if measured_c > temp_max:
            return TemperatureDeviation(
                item_id=item_id,
                depot_id=depot_id,
                source=source,
                direction=DeviationDirection.ABOVE_MAX,
                measured_c=measured_c,
                limit_c=temp_max,
                magnitude_c=round(measured_c - temp_max, 4),
            )
        return None

    @staticmethod
    def _latest_by_zone(
        readings: list[DepotZoneTemperature],
    ) -> dict[str, DepotZoneTemperature]:
        index: dict[str, DepotZoneTemperature] = {}
        for r in readings:
            cur = index.get(r.zone_id)
            if cur is None or r.measured_at >= cur.measured_at:
                index[r.zone_id] = r
        return index

    @staticmethod
    def _latest_by_vehicle(
        readings: list[VehicleTemperatureReading],
    ) -> dict[str, VehicleTemperatureReading]:
        index: dict[str, VehicleTemperatureReading] = {}
        for r in readings:
            cur = index.get(r.vehicle_id)
            if cur is None or r.measured_at >= cur.measured_at:
                index[r.vehicle_id] = r
        return index
