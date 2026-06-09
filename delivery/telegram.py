"""TelegramNotifier — Telegram Bot API ile gönderim (httpx).

Ortam: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID. Aciliyet skoru orta/yüksek
bildirimler için uygun (hızlı, ucuz). httpx lazy import edilir.
"""

from __future__ import annotations

import os

from delivery.base import Notifier
from delivery.errors import DeliveryError


class TelegramNotifier(Notifier):
    channel = "telegram"

    def __init__(
        self,
        bot_token: str | None = None,
        chat_id: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.timeout = timeout

    def send(self, message: str, payload: dict) -> dict:
        if not self.bot_token or not self.chat_id:
            raise DeliveryError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID tanımlı değil.")
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover
            raise DeliveryError("httpx kurulu değil.") from exc
        try:
            resp = httpx.post(
                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                json={"chat_id": self.chat_id, "text": message},
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            raise DeliveryError(f"Telegram gönderimi başarısız: {exc}") from exc
        return {"channel": self.channel, "status": "sent", "message": message}
