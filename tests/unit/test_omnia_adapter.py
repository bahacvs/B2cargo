"""MockOmniaAdapter ve stok kaynağı factory testleri (Omnia geçişi)."""

from __future__ import annotations

import pytest

from adapters import factory
from adapters.errors import AdapterError
from adapters.omnia.mock import MockOmniaAdapter
from models.stock import DepotSnapshot


def test_omnia_loads_stock_from_mock_data():
    snap = MockOmniaAdapter().fetch_stock("ankara")
    assert isinstance(snap, DepotSnapshot)
    assert any(i.item_id == "ank-frozen-001" for i in snap.items)


def test_omnia_fail_depot_raises():
    with pytest.raises(AdapterError):
        MockOmniaAdapter(fail_depots={"ankara"}).fetch_stock("ankara")


def test_factory_defaults_to_omnia(monkeypatch):
    monkeypatch.setenv("USE_MOCK_ADAPTERS", "true")
    monkeypatch.delenv("STOCK_SOURCE", raising=False)
    assert isinstance(factory.get_stock_adapter(), MockOmniaAdapter)


def test_factory_can_select_devambar(monkeypatch):
    from adapters.devambar.mock import MockDevambarAdapter

    monkeypatch.setenv("USE_MOCK_ADAPTERS", "true")
    monkeypatch.setenv("STOCK_SOURCE", "devambar")
    assert isinstance(factory.get_stock_adapter(), MockDevambarAdapter)
