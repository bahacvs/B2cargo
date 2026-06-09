"""Bildirim kanalı interface'i (Notifier).

NotificationBuilder payload üretir; Notifier o payload'ı bir kanaldan (WhatsApp,
Telegram) GÖNDERİR. Adapter deseniyle aynı mantık: interface değişmez, kanal
implementasyonu (mock/gerçek) değişir.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Notifier(ABC):
    """Tek bir kanaldan bildirim gönderen soyut sınıf."""

    @abstractmethod
    def send(self, message: str, payload: dict) -> dict:
        """Mesajı gönderir; gönderim sonucunu (durum/kanal) döner.

        Hata durumunda DeliveryError fırlatır — dispatcher izole eder.
        """


class NullNotifier(Notifier):
    """Gönderim yapmayan kanal (örn. dashboard — UI zaten API'den okur)."""

    def __init__(self, channel: str = "null") -> None:
        self.channel = channel

    def send(self, message: str, payload: dict) -> dict:
        return {"channel": self.channel, "status": "skipped", "message": message}
