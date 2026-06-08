"""NotificationBuilder — bildirim payload'ı üretir, GÖNDERMEZ. Adım 9.

Kurallar config/notification_rules.json'dan: seviye → kanal eşlemesi, throttle
(max_per_run). LOW seviye kanal almaz. Çıktı `notifications` tablosuna/kuyruğa
yazılmaya hazır payload listesidir.
"""

from __future__ import annotations

from config import load_notification_rules
from models.reports import DepotRiskReport
from models.risk import RiskLevel, RiskResult


class NotificationBuilder:
    def __init__(self, rules: dict | None = None) -> None:
        self._rules = rules or load_notification_rules()
        self._channels: dict[str, list[str]] = self._rules.get("channels", {})
        self._max_per_run: int = self._rules.get("throttle", {}).get("max_per_run", 50)

    def build(self, report: DepotRiskReport) -> list[dict]:
        """En kritikten başlayarak kanal bazlı payload listesi üretir."""

        riskli = [r for r in report.results if r.level is not RiskLevel.LOW]
        riskli.sort(key=lambda r: r.score, reverse=True)

        payloads: list[dict] = []
        for result in riskli:
            for channel in self._channels.get(result.level.value, []):
                payloads.append(self._payload(report.depot_id, result, channel))
                if len(payloads) >= self._max_per_run:
                    return payloads
        return payloads

    @staticmethod
    def _payload(depot_id: str, result: RiskResult, channel: str) -> dict:
        return {
            "depot_id": depot_id,
            "item_id": result.item_id,
            "level": result.level.value,
            "channel": channel,
            "score": result.score,
            "reasons": [r.code for r in result.reasons],
            "status": "pending",
        }
