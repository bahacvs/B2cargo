"""ArventoApiAdapter — gerçek (prod) implementasyon, STUB (adım 14)."""

from __future__ import annotations

from adapters.arvento.client import ArventoClient
from adapters.base import ArventoAdapter
from models.temperature import VehicleTemperatureReading


class ArventoApiAdapter(ArventoAdapter):
    def __init__(self, client: ArventoClient | None = None) -> None:
        self._client = client or ArventoClient()

    def fetch_vehicle_temps(self, depot_id: str) -> list[VehicleTemperatureReading]:
        # TODO(adım 14): client çıktısını VehicleTemperatureReading'e map et.
        raise NotImplementedError(
            "Arvento gerçek adapter henüz uygulanmadı (adım 14). "
            "Geliştirmede MockArventoAdapter kullanın."
        )
