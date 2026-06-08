"""MockArventoAdapter — araç içi sıcaklık okumaları, gerçek API olmadan."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from adapters._mock_loader import DEFAULT_DATA_DIR, load_json
from adapters.base import ArventoAdapter
from adapters.errors import AdapterError
from models.temperature import VehicleTemperatureReading


class MockArventoAdapter(ArventoAdapter):
    def __init__(
        self,
        readings: dict[str, list[VehicleTemperatureReading]] | None = None,
        data_dir: str | Path = DEFAULT_DATA_DIR,
        fail_depots: Iterable[str] | None = None,
    ) -> None:
        self._readings = readings or {}
        self._data_dir = Path(data_dir)
        self._fail_depots = set(fail_depots or [])

    def fetch_vehicle_temps(self, depot_id: str) -> list[VehicleTemperatureReading]:
        if depot_id in self._fail_depots:
            raise AdapterError(f"Arvento API erişilemedi: {depot_id}")

        if depot_id in self._readings:
            return self._readings[depot_id]

        raw = load_json(self._data_dir, depot_id, "vehicle")
        return [VehicleTemperatureReading(**row) for row in (raw or [])]
