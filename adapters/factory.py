"""Adapter factory — mock/prod seçimi tek yerde.

`USE_MOCK_ADAPTERS` ortam değişkenine göre uygun implementasyonu döner. Çağıran
kodun hiçbir yerinde mock/prod `if`'i dağılmaz; herkes bu factory'i kullanır.
"""

from __future__ import annotations

import os

from adapters.arvento.adapter import ArventoApiAdapter
from adapters.arvento.mock import MockArventoAdapter
from adapters.base import ArventoAdapter, DevambarAdapter, SensorAdapter
from adapters.devambar.adapter import DevambarApiAdapter
from adapters.devambar.mock import MockDevambarAdapter
from adapters.sensor.adapter import SensorApiAdapter
from adapters.sensor.mock import MockSensorAdapter


def _use_mock() -> bool:
    return os.getenv("USE_MOCK_ADAPTERS", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_devambar_adapter() -> DevambarAdapter:
    return MockDevambarAdapter() if _use_mock() else DevambarApiAdapter()


def get_sensor_adapter() -> SensorAdapter:
    return MockSensorAdapter() if _use_mock() else SensorApiAdapter()


def get_arvento_adapter() -> ArventoAdapter:
    return MockArventoAdapter() if _use_mock() else ArventoApiAdapter()
