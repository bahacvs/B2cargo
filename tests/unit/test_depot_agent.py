"""DepotAgent birleştirme testleri (adım 10).

API anahtarı yokken ExplanationAgent başarısız olur → TemplateExplanation fallback.
"""

from __future__ import annotations

import pytest

from adapters.devambar.mock import MockDevambarAdapter
from adapters.sensor.mock import MockSensorAdapter
from agents.depot_agent import DepotAgent
from config import load_depots
from models.risk import RiskLevel


@pytest.fixture(autouse=True)
def _no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def _ankara_agent() -> DepotAgent:
    return DepotAgent(config=load_depots()["ankara"])


def test_depot_agent_produces_full_report():
    snapshot = MockDevambarAdapter().fetch_stock("ankara")
    temps = MockSensorAdapter().fetch_depot_temps("ankara")
    report = _ankara_agent().run(snapshot, depot_temps=temps)

    assert report.depot_id == "ankara"
    assert report.depot_name == "Ankara Depo"
    assert len(report.results) == 5
    by_id = {r.item_id: r for r in report.results}
    assert by_id["ank-frozen-001"].level is RiskLevel.CRITICAL


def test_explanation_falls_back_to_template():
    snapshot = MockDevambarAdapter().fetch_stock("ankara")
    temps = MockSensorAdapter().fetch_depot_temps("ankara")
    report = _ankara_agent().run(snapshot, depot_temps=temps)
    # Claude yok → template özet üretilir (boş değil, "kritik" içerir).
    assert report.explanation
    assert "kritik" in report.explanation


def test_actions_and_notifications_present():
    snapshot = MockDevambarAdapter().fetch_stock("ankara")
    temps = MockSensorAdapter().fetch_depot_temps("ankara")
    report = _ankara_agent().run(snapshot, depot_temps=temps)
    # Kritik donuk et için aksiyon ve bildirim üretilmeli.
    assert any(a["item_id"] == "ank-frozen-001" for a in report.actions)
    assert any(n["item_id"] == "ank-frozen-001" for n in report.notifications)


def test_pipeline_survives_when_no_temps():
    # Sensor verisi yok → sıcaklık riski yok ama rapor yine üretilir (diğer riskler).
    snapshot = MockDevambarAdapter().fetch_stock("ankara")
    report = _ankara_agent().run(snapshot, depot_temps=[])
    assert len(report.results) == 5
    # Donuk et artık kritik değil (sapma sinyali yok), ama rapor sağlam.
    assert report.data_quality_alerts  # izlenen kalemler için ölçüm yok uyarısı
