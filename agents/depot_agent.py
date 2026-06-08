"""DepotAgent — 11 ajan = 1 kod. Config ile örneklenir. Adım 10.

Alt ajanları sırayla çalıştırıp tek bir `DepotRiskReport` üretir:
  TemperatureMonitor → StockRisk → Explanation(+fallback) → Action → NotificationBuilder

Her AI/dış ajan çağrısı `safe_run_agent` ile sarılır — biri çökse de rapor üretilir
(CLAUDE.md "pipeline durmamalı"). Deterministik çekirdek (monitor + risk) doğrudan
çağrılır; onlar zaten sıfır-AI ve güvenilir.

```python
depot_agents = {
    depot_id: DepotAgent(config=DEPOT_CONFIGS[depot_id])
    for depot_id in ALL_DEPOT_IDS
}
```
"""

from __future__ import annotations

from collections.abc import Iterable

from agents.sub_agents.action import ActionAgent
from agents.sub_agents.explanation import ExplanationAgent, TemplateExplanation
from agents.sub_agents.notification_builder import NotificationBuilder
from agents.sub_agents.stock_risk import StockRiskAgent
from agents.sub_agents.temperature_monitor import TemperatureMonitorAgent
from models.reports import DepotRiskReport
from models.stock import DepotSnapshot
from models.temperature import DepotZoneTemperature, VehicleTemperatureReading
from orchestration.safe import safe_run_agent


class DepotAgent:
    def __init__(
        self,
        config: dict,
        *,
        temperature_monitor: TemperatureMonitorAgent | None = None,
        stock_risk: StockRiskAgent | None = None,
        explanation: ExplanationAgent | None = None,
        template_explanation: TemplateExplanation | None = None,
        action: ActionAgent | None = None,
        notification_builder: NotificationBuilder | None = None,
    ) -> None:
        self.config = config
        self.depot_id = config["id"]
        self.depot_name = config.get("name", self.depot_id)

        self._monitor = temperature_monitor or TemperatureMonitorAgent()
        self._risk = stock_risk or StockRiskAgent()
        self._explanation = explanation or ExplanationAgent()
        self._template = template_explanation or TemplateExplanation()
        self._action = action or ActionAgent()
        self._notifications = notification_builder or NotificationBuilder()

    def run(
        self,
        snapshot: DepotSnapshot,
        depot_temps: list[DepotZoneTemperature] | None = None,
        vehicle_temps: list[VehicleTemperatureReading] | None = None,
        delayed_shipments: Iterable[str] | None = None,
    ) -> DepotRiskReport:
        # 1-2) Deterministik çekirdek (sıfır AI) — doğrudan çağrılır.
        monitor = self._monitor.run(
            snapshot, depot_temps=depot_temps, vehicle_temps=vehicle_temps
        )
        results = self._risk.assess(
            snapshot,
            deviations=monitor.deviations,
            delayed_shipments=delayed_shipments,
        )

        report = DepotRiskReport(
            depot_id=self.depot_id,
            depot_name=self.depot_name,
            results=results,
            data_quality_alerts=monitor.alerts,
        )

        # 3) Açıklama: Claude → başarısızsa template (her ikisi de aynı imza).
        report.explanation = (
            safe_run_agent(
                self._explanation.generate,
                self._template.generate,
                depot_name=self.depot_name,
                results=results,
            )
            or ""
        )

        # 4) Aksiyonlar (kural tabanlı, güvenli).
        report.actions = (
            safe_run_agent(
                self._action.recommend,
                depot_name=self.depot_name,
                results=results,
            )
            or []
        )

        # 5) Bildirim payload'ları.
        report.notifications = (
            safe_run_agent(self._notifications.build, report=report) or []
        )

        return report
