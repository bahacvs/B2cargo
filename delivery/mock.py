"""MockNotifier — gerçek API olmadan gönderim (geliştirme + test).

Gönderilen mesajları bellekte tutar; testler `sent` listesini doğrular.
"""

from __future__ import annotations

from delivery.base import Notifier


class MockNotifier(Notifier):
    def __init__(self, channel: str = "mock") -> None:
        self.channel = channel
        self.sent: list[dict] = []

    def send(self, message: str, payload: dict) -> dict:
        record = {
            "channel": self.channel,
            "status": "sent",
            "message": message,
            "item_id": payload.get("item_id"),
            "level": payload.get("level"),
        }
        self.sent.append(record)
        return record
