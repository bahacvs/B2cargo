"""SensorApiAdapter — gerçek (prod) implementasyon. Adım 14."""

from __future__ import annotations

from adapters.base import SensorAdapter
from adapters.sensor.client import SensorClient
from models.temperature import DepotZoneTemperature


class SensorApiAdapter(SensorAdapter):
    def __init__(self, client: SensorClient | None = None) -> None:
        self._client = client or SensorClient()

    def fetch_depot_temps(self, depot_id: str) -> list[DepotZoneTemperature]:
        rows = self._client.get_depot_temps(depot_id)
        result = []
        for row in rows:
            data = {"depot_id": depot_id, "zone_id": row["zone_id"], "temp_c": row["temp_c"]}
            if row.get("measured_at"):
                data["measured_at"] = row["measured_at"]
            result.append(DepotZoneTemperature(**data))
        return result
