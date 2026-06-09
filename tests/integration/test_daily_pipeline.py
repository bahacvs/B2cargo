"""Günlük pipeline entegrasyon testleri (adım 12) — hata izolasyonu dahil."""

from __future__ import annotations

import pytest

from adapters.arvento.mock import MockArventoAdapter
from adapters.omnia.mock import MockOmniaAdapter
from adapters.sensor.mock import MockSensorAdapter
from config import all_depot_ids
from models.risk import RiskLevel
from orchestration.daily_pipeline import run_daily_pipeline


@pytest.fixture(autouse=True)
def _no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def _adapters(devambar_fail=None, sensor_fail=None):
    # Stok kaynağı artık Omnia (mock).
    return dict(
        stock=MockOmniaAdapter(fail_depots=devambar_fail),
        sensor=MockSensorAdapter(fail_depots=sensor_fail),
        arvento=MockArventoAdapter(),
    )


def test_all_eleven_depots_consolidated():
    report = run_daily_pipeline(**_adapters())
    assert len(report.depot_reports) == len(all_depot_ids()) == 11
    # ankara'da donuk et kritik → ankara öncelik sıralamasında üstlerde.
    assert "ankara" in report.prioritized_depots[:3]


def test_devambar_failure_skips_depot_others_continue():
    report = run_daily_pipeline(**_adapters(devambar_fail={"ankara"}))
    ids = {r.depot_id for r in report.depot_reports}
    assert "ankara" not in ids  # depo atlandı
    assert len(report.depot_reports) == 10  # diğer 10 devam etti


def test_sensor_failure_falls_back_depot_still_processed():
    report = run_daily_pipeline(depot_ids=["ankara"], **_adapters(sensor_fail={"ankara"}))
    assert len(report.depot_reports) == 1
    depot = report.depot_reports[0]
    # Sensor yok → sıcaklık sapması yok ama rapor üretildi (diğer riskler işlendi).
    assert len(depot.results) == 5


def test_single_depot_run():
    report = run_daily_pipeline(depot_ids=["ankara"], **_adapters())
    assert [r.depot_id for r in report.depot_reports] == ["ankara"]
    by_id = {r.item_id: r for r in report.depot_reports[0].results}
    assert by_id["ank-frozen-001"].level is RiskLevel.CRITICAL
