"""TemperatureMonitorAgent birim testleri (saf kural, sıfır AI)."""

from __future__ import annotations

from agents.sub_agents.temperature_monitor import TemperatureMonitorAgent
from models.signals import DeviationDirection, DeviationSource
from models.stock import DepotSnapshot, StockItem
from models.temperature import DepotZoneTemperature, VehicleTemperatureReading


def _snapshot(*items: StockItem) -> DepotSnapshot:
    return DepotSnapshot(depot_id="ankara", items=list(items))


def _item(**kw) -> StockItem:
    base = {"item_id": "i1", "name": "X", "depot_id": "ankara"}
    base.update(kw)
    return StockItem(**base)


def test_frozen_below_min_emits_below_min_deviation():
    item = _item(temp_min_c=-18, temp_max_c=-15, zone_id="frozen")
    temps = [DepotZoneTemperature(depot_id="ankara", zone_id="frozen", temp_c=-25)]
    res = TemperatureMonitorAgent().run(_snapshot(item), depot_temps=temps)
    assert len(res.deviations) == 1
    dev = res.deviations[0]
    assert dev.direction is DeviationDirection.BELOW_MIN
    assert dev.source is DeviationSource.DEPOT_ZONE
    assert dev.magnitude_c == 7  # -18 - (-25)


def test_zone_above_max_emits_above_max_deviation():
    item = _item(temp_min_c=-18, temp_max_c=-15, zone_id="frozen")
    temps = [DepotZoneTemperature(depot_id="ankara", zone_id="frozen", temp_c=-10)]
    res = TemperatureMonitorAgent().run(_snapshot(item), depot_temps=temps)
    assert res.deviations[0].direction is DeviationDirection.ABOVE_MAX
    assert res.deviations[0].magnitude_c == 5  # -10 - (-15)


def test_within_range_no_deviation_no_alert():
    item = _item(temp_min_c=2, temp_max_c=8, zone_id="cold")
    temps = [DepotZoneTemperature(depot_id="ankara", zone_id="cold", temp_c=5)]
    res = TemperatureMonitorAgent().run(_snapshot(item), depot_temps=temps)
    assert res.deviations == []
    assert res.alerts == []


def test_dry_goods_skipped_entirely():
    item = _item(zone_id="ambient")  # temp bounds null → izlenmez
    temps = [DepotZoneTemperature(depot_id="ankara", zone_id="ambient", temp_c=40)]
    res = TemperatureMonitorAgent().run(_snapshot(item), depot_temps=temps)
    assert res.deviations == []
    assert res.alerts == []


def test_vehicle_temperature_deviation():
    item = _item(temp_min_c=2, temp_max_c=8, vehicle_id="v1", shipment_id="s1")
    veh = [VehicleTemperatureReading(vehicle_id="v1", shipment_id="s1", temp_c=14)]
    res = TemperatureMonitorAgent().run(_snapshot(item), vehicle_temps=veh)
    assert res.deviations[0].source is DeviationSource.VEHICLE
    assert res.deviations[0].magnitude_c == 6


def test_missing_temperature_data_emits_quality_alert():
    item = _item(temp_min_c=2, temp_max_c=8, zone_id="cold")
    res = TemperatureMonitorAgent().run(_snapshot(item))  # hiç ölçüm yok
    assert res.deviations == []
    assert len(res.alerts) == 1
    assert res.alerts[0].code == "NO_TEMPERATURE_DATA"


def test_sensor_down_vehicle_signals_still_processed():
    # Depo zonu olan kalem → alert; aracı olan kalem → sapma. İkisi de işlenir.
    zone_item = _item(item_id="z", temp_min_c=2, temp_max_c=8, zone_id="cold")
    veh_item = _item(
        item_id="v", temp_min_c=2, temp_max_c=8, vehicle_id="v1", shipment_id="s1"
    )
    veh = [VehicleTemperatureReading(vehicle_id="v1", temp_c=14)]
    res = TemperatureMonitorAgent().run(
        _snapshot(zone_item, veh_item), depot_temps=[], vehicle_temps=veh
    )
    assert len(res.deviations) == 1 and res.deviations[0].item_id == "v"
    assert len(res.alerts) == 1 and res.alerts[0].item_id == "z"


def test_latest_zone_reading_wins():
    from datetime import datetime, timedelta

    item = _item(temp_min_c=2, temp_max_c=8, zone_id="cold")
    now = datetime(2026, 6, 8, 12, 0, 0)
    temps = [
        DepotZoneTemperature(depot_id="ankara", zone_id="cold", temp_c=5, measured_at=now - timedelta(hours=1)),
        DepotZoneTemperature(depot_id="ankara", zone_id="cold", temp_c=20, measured_at=now),
    ]
    res = TemperatureMonitorAgent().run(_snapshot(item), depot_temps=temps)
    assert len(res.deviations) == 1  # en güncel (20°C) baz alınır


def test_both_zone_and_vehicle_deviation_for_same_item():
    item = _item(
        temp_min_c=2, temp_max_c=8, zone_id="cold", vehicle_id="v1", shipment_id="s1"
    )
    temps = [DepotZoneTemperature(depot_id="ankara", zone_id="cold", temp_c=12)]
    veh = [VehicleTemperatureReading(vehicle_id="v1", temp_c=15)]
    res = TemperatureMonitorAgent().run(
        _snapshot(item), depot_temps=temps, vehicle_temps=veh
    )
    sources = {d.source for d in res.deviations}
    assert sources == {DeviationSource.DEPOT_ZONE, DeviationSource.VEHICLE}


def test_all_normal_produces_nothing():
    items = [
        _item(item_id="a", temp_min_c=2, temp_max_c=8, zone_id="cold"),
        _item(item_id="b", zone_id="ambient"),  # kuru gıda
    ]
    temps = [DepotZoneTemperature(depot_id="ankara", zone_id="cold", temp_c=5)]
    res = TemperatureMonitorAgent().run(_snapshot(*items), depot_temps=temps)
    assert res.deviations == []
    assert res.alerts == []
