"""Adapter factory — mock/prod ve stok kaynağı seçimi tek yerde.

- USE_MOCK_ADAPTERS: mock/prod implementasyonu seçer (geliştirmede true).
- STOCK_SOURCE: stok/sevkiyat kaynağı (omnia | devambar). B2 Cargo Omnia'ya geçti,
  varsayılan "omnia". Devambar artık yalnızca DB (bağlantı sonra netleşecek).

Çağıran kodun hiçbir yerinde mock/prod ya da kaynak `if`'i dağılmaz; herkes bu
factory'i kullanır.
"""

from __future__ import annotations

import os

from adapters.arvento.adapter import ArventoApiAdapter
from adapters.arvento.mock import MockArventoAdapter
from adapters.base import ArventoAdapter, SensorAdapter, StockAdapter
from adapters.devambar.adapter import DevambarApiAdapter
from adapters.devambar.mock import MockDevambarAdapter
from adapters.omnia.adapter import OmniaApiAdapter
from adapters.omnia.mock import MockOmniaAdapter
from adapters.sensor.adapter import SensorApiAdapter
from adapters.sensor.mock import MockSensorAdapter


def _use_mock() -> bool:
    return os.getenv("USE_MOCK_ADAPTERS", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_stock_adapter() -> StockAdapter:
    """Stok/sevkiyat kaynağı (STOCK_SOURCE: omnia varsayılan, devambar opsiyonel)."""

    source = os.getenv("STOCK_SOURCE", "omnia").strip().lower()
    if source == "devambar":
        return MockDevambarAdapter() if _use_mock() else DevambarApiAdapter()
    # Varsayılan: Omnia.
    return MockOmniaAdapter() if _use_mock() else OmniaApiAdapter()


# Geriye dönük uyum (eski çağrılar Devambar'ı doğrudan istiyorsa).
def get_devambar_adapter() -> StockAdapter:
    return MockDevambarAdapter() if _use_mock() else DevambarApiAdapter()


def get_sensor_adapter() -> SensorAdapter:
    return MockSensorAdapter() if _use_mock() else SensorApiAdapter()


def get_arvento_adapter() -> ArventoAdapter:
    return MockArventoAdapter() if _use_mock() else ArventoApiAdapter()
