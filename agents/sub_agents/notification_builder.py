"""NotificationBuilder — bildirim payload'ı üretir, GÖNDERMEZ. STUB (adım 9).

Kurallar config/notification_rules.json'dan gelir (seviye → kanal eşlemesi).
"""

from __future__ import annotations

from models.reports import DepotRiskReport


class NotificationBuilder:
    def build(self, report: DepotRiskReport) -> list[dict]:
        # TODO(adım 9): notification_rules.json'a göre payload listesi üret.
        raise NotImplementedError("NotificationBuilder henüz uygulanmadı (adım 9).")
