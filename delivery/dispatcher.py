"""NotificationDispatcher — payload'ları kanala göre teslim eder.

Kanal seçimi NotificationBuilder tarafından (notification_rules.json, aciliyet
skoruna göre) önceden yapılmıştır; dispatcher her payload'ı `channel` alanına göre
ilgili Notifier'a yönlendirir. Bir kanal çökse de diğerleri devam eder (pipeline
durmamalı) — DeliveryError yakalanır, loglanır.
"""

from __future__ import annotations

import logging

from delivery.base import Notifier
from delivery.errors import DeliveryError
from models.reports import DepotRiskReport

logger = logging.getLogger("axiom.delivery")

_LEVEL_TR = {"CRITICAL": "KRİTİK", "HIGH": "YÜKSEK", "MEDIUM": "ORTA", "LOW": "DÜŞÜK"}


def format_message(payload: dict) -> str:
    """Payload'dan kısa Türkçe bildirim metni üretir."""

    level = _LEVEL_TR.get(payload.get("level", ""), payload.get("level", ""))
    reasons = ", ".join(payload.get("reasons", [])) or "-"
    return (
        f"[{level}] {payload.get('depot_id')} · {payload.get('item_id')} "
        f"— risk skoru {payload.get('score', 0):.0f}. Gerekçe: {reasons}."
    )


class NotificationDispatcher:
    def __init__(self, notifiers: dict[str, Notifier]) -> None:
        self._notifiers = notifiers

    def dispatch(self, payloads: list[dict]) -> list[dict]:
        results: list[dict] = []
        for payload in payloads:
            channel = payload.get("channel", "")
            notifier = self._notifiers.get(channel)
            if notifier is None:
                logger.warning("Tanımsız kanal, atlandı: %s", channel)
                continue
            message = format_message(payload)
            try:
                results.append(notifier.send(message, payload))
            except DeliveryError as exc:
                logger.error("%s gönderimi başarısız: %s", channel, exc)
                results.append(
                    {"channel": channel, "status": "failed", "error": str(exc)}
                )
        return results

    def send_text(self, channel: str, message: str) -> dict | None:
        """Tek bir kanala serbest metin gönderir (örn. günlük özet → Telegram)."""

        notifier = self._notifiers.get(channel)
        if notifier is None:
            return None
        try:
            return notifier.send(message, {"channel": channel, "level": "REPORT"})
        except DeliveryError as exc:
            logger.error("%s özet gönderimi başarısız: %s", channel, exc)
            return {"channel": channel, "status": "failed", "error": str(exc)}


def dispatch_report(
    report: DepotRiskReport, dispatcher: NotificationDispatcher | None = None
) -> list[dict]:
    """Bir deponun bildirim payload'larını teslim eder."""

    from delivery.factory import get_dispatcher

    dispatcher = dispatcher or get_dispatcher()
    return dispatcher.dispatch(report.notifications)


def dispatch_turkey(report, dispatcher: NotificationDispatcher | None = None) -> list[dict]:
    """Tüm depo bildirimlerini teslim eder + yönetici özetini Telegram'a yollar."""

    from delivery.factory import get_dispatcher

    dispatcher = dispatcher or get_dispatcher()
    results: list[dict] = []
    for depot in report.depot_reports:
        results.extend(dispatcher.dispatch(depot.notifications))
    if report.executive_summary:
        summary = dispatcher.send_text("telegram", report.executive_summary)
        if summary:
            results.append(summary)
    return results
