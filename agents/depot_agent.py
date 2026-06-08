"""DepotAgent — 11 ajan = 1 kod. Config ile örneklenir. STUB (adım 10).

```python
depot_agents = {
    depot_id: DepotAgent(config=DEPOT_CONFIGS[depot_id])
    for depot_id in ALL_DEPOT_IDS
}
```

Alt ajanları (TemperatureMonitor → StockRisk → Explanation → Action →
NotificationBuilder) sırayla çalıştırıp `DepotRiskReport` üretir. Her alt ajan
çağrısı `safe_run_agent` ile sarılır (pipeline durmaz). Deterministik çekirdek
(TemperatureMonitor + StockRisk) hazır; bu sınıf onları birleştirir.
"""

from __future__ import annotations

from models.reports import DepotRiskReport
from models.stock import DepotSnapshot
from models.temperature import DepotZoneTemperature, VehicleTemperatureReading


class DepotAgent:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.depot_id = config["id"]

    def run(
        self,
        snapshot: DepotSnapshot,
        depot_temps: list[DepotZoneTemperature] | None = None,
        vehicle_temps: list[VehicleTemperatureReading] | None = None,
    ) -> DepotRiskReport:
        # TODO(adım 10): TemperatureMonitorAgent.run → StockRiskAgent.assess →
        # ExplanationAgent (fallback) → ActionAgent → NotificationBuilder
        # sonuçlarını DepotRiskReport içinde birleştir.
        raise NotImplementedError("DepotAgent birleştirme henüz uygulanmadı (adım 10).")
