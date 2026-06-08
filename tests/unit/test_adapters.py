"""Mock adapter ve factory testleri.

Senaryolar: mock JSON yükleme, bellek içi override, API çökmesi (AdapterError),
factory'nin USE_MOCK_ADAPTERS'a göre mock döndürmesi.
"""

from __future__ import annotations

import pytest

from adapters import factory
from adapters.arvento.mock import MockArventoAdapter
from adapters.devambar.mock import MockDevambarAdapter
from adapters.errors import AdapterError
from adapters.sensor.mock import MockSensorAdapter
from models.stock import DepotSnapshot, StockItem


def test_mock_devambar_loads_from_json():
    snap = MockDevambarAdapter().fetch_stock("ankara")
    assert isinstance(snap, DepotSnapshot)
    ids = {i.item_id for i in snap.items}
    assert "ank-frozen-001" in ids


def test_mock_devambar_unknown_depot_returns_empty_snapshot():
    snap = MockDevambarAdapter().fetch_stock("yok-boyle-depo")
    assert snap.items == []


def test_mock_devambar_in_memory_override():
    item = StockItem(item_id="x", name="X", depot_id="ankara")
    snaps = {"ankara": DepotSnapshot(depot_id="ankara", items=[item])}
    snap = MockDevambarAdapter(snapshots=snaps).fetch_stock("ankara")
    assert snap.items[0].item_id == "x"


def test_mock_devambar_fail_depot_raises():
    adapter = MockDevambarAdapter(fail_depots={"ankara"})
    with pytest.raises(AdapterError):
        adapter.fetch_stock("ankara")


def test_mock_sensor_loads_temps():
    temps = MockSensorAdapter().fetch_depot_temps("ankara")
    zones = {t.zone_id for t in temps}
    assert {"frozen", "cold", "ambient"} <= zones


def test_mock_sensor_fail_raises():
    with pytest.raises(AdapterError):
        MockSensorAdapter(fail_depots={"ankara"}).fetch_depot_temps("ankara")


def test_mock_arvento_unknown_depot_returns_empty():
    assert MockArventoAdapter().fetch_vehicle_temps("ankara") == []


def test_factory_returns_mock_when_enabled(monkeypatch):
    monkeypatch.setenv("USE_MOCK_ADAPTERS", "true")
    assert isinstance(factory.get_devambar_adapter(), MockDevambarAdapter)
    assert isinstance(factory.get_sensor_adapter(), MockSensorAdapter)
    assert isinstance(factory.get_arvento_adapter(), MockArventoAdapter)


def test_factory_returns_prod_when_disabled(monkeypatch):
    monkeypatch.setenv("USE_MOCK_ADAPTERS", "false")
    # Prod adapter'lar stub; sadece tip seçimini doğruluyoruz (çağırmıyoruz).
    assert not isinstance(factory.get_devambar_adapter(), MockDevambarAdapter)
