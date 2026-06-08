"""ArventoApiAdapter — gerçek (prod) implementasyon. Adım 14."""

from __future__ import annotations

from adapters.arvento.client import ArventoClient
from adapters.base import ArventoAdapter
from models.temperature import VehicleTemperatureReading


class ArventoApiAdapter(ArventoAdapter):
    def __init__(self, client: ArventoClient | None = None) -> None:
        self._client = client or ArventoClient()

    def fetch_vehicle_temps(self, depot_id: str) -> list[VehicleTemperatureReading]:
        rows = self._client.get_vehicle_temps(depot_id)
        result = []
        for row in rows:
            data = {"vehicle_id": row["vehicle_id"], "temp_c": row["temp_c"]}
            if row.get("shipment_id"):
                data["shipment_id"] = row["shipment_id"]
            if row.get("measured_at"):
                data["measured_at"] = row["measured_at"]
            result.append(VehicleTemperatureReading(**data))
        return result
