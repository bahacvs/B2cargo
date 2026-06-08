"""SensorApiAdapter — gerçek (prod) implementasyon, STUB (adım 14)."""

from __future__ import annotations

from adapters.base import SensorAdapter
from adapters.sensor.client import SensorClient
from models.temperature import DepotZoneTemperature


class SensorApiAdapter(SensorAdapter):
    def __init__(self, client: SensorClient | None = None) -> None:
        self._client = client or SensorClient()

    def fetch_depot_temps(self, depot_id: str) -> list[DepotZoneTemperature]:
        # TODO(adım 14): client çıktısını DepotZoneTemperature'a map et.
        raise NotImplementedError(
            "Sensor gerçek adapter henüz uygulanmadı (adım 14). "
            "Geliştirmede MockSensorAdapter kullanın."
        )
