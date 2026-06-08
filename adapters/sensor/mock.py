"""MockSensorAdapter — depo zon sıcaklıkları, gerçek API olmadan.

`fail_depots` ile "Sensor cevap vermezse fallback" senaryosu test edilir.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from adapters._mock_loader import DEFAULT_DATA_DIR, load_json
from adapters.base import SensorAdapter
from adapters.errors import AdapterError
from models.temperature import DepotZoneTemperature


class MockSensorAdapter(SensorAdapter):
    def __init__(
        self,
        readings: dict[str, list[DepotZoneTemperature]] | None = None,
        data_dir: str | Path = DEFAULT_DATA_DIR,
        fail_depots: Iterable[str] | None = None,
    ) -> None:
        self._readings = readings or {}
        self._data_dir = Path(data_dir)
        self._fail_depots = set(fail_depots or [])

    def fetch_depot_temps(self, depot_id: str) -> list[DepotZoneTemperature]:
        if depot_id in self._fail_depots:
            raise AdapterError(f"Sensor API erişilemedi: {depot_id}")

        if depot_id in self._readings:
            return self._readings[depot_id]

        raw = load_json(self._data_dir, depot_id, "temps")
        return [DepotZoneTemperature(**row) for row in (raw or [])]
