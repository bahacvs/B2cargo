"""Entegrasyon: mock adapter → TemperatureMonitor → StockRisk uçtan uca.

Gerçek mock_data/depots/ankara_*.json üzerinde deterministik çekirdeği çalıştırır.
Donuk bölge -10°C (max -15 aşıldı) → kritik kalem beklenir.
"""

from __future__ import annotations

from datetime import date

from adapters.factory import get_devambar_adapter, get_sensor_adapter
from agents.sub_agents.stock_risk import StockRiskAgent
from agents.sub_agents.temperature_monitor import TemperatureMonitorAgent
from models.risk import RiskLevel


def test_ankara_core_pipeline_produces_critical_frozen_item():
    snapshot = get_devambar_adapter().fetch_stock("ankara")
    depot_temps = get_sensor_adapter().fetch_depot_temps("ankara")

    monitor = TemperatureMonitorAgent().run(snapshot, depot_temps=depot_temps)
    results = StockRiskAgent().assess(
        snapshot, deviations=monitor.deviations, today=date(2026, 6, 8)
    )

    by_id = {r.item_id: r for r in results}
    # Donuk et bölgesi -10°C, izin -18..-15 → ABOVE_MAX sapması → kritik.
    assert by_id["ank-frozen-001"].level is RiskLevel.CRITICAL
    # Kuru gıda (pirinç) sıcaklık izlenmez, normal stok → düşük.
    assert by_id["ank-amb-001"].level is RiskLevel.LOW
    # En az bir veri kalitesi uyarısı yok (tüm izlenen kalemlerin ölçümü var).
    assert monitor.alerts == []
