"""WhatsAppNotifier — WhatsApp Cloud API ile gönderim (httpx).

Ortam: WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_RECIPIENT.
En yüksek aciliyet (kritik) bildirimleri için — anlık, kişisel kanal.
"""

from __future__ import annotations

import os

from delivery.base import Notifier
from delivery.errors import DeliveryError


class WhatsAppNotifier(Notifier):
    channel = "whatsapp"

    def __init__(
        self,
        token: str | None = None,
        phone_number_id: str | None = None,
        recipient: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.token = token or os.getenv("WHATSAPP_TOKEN", "")
        self.phone_number_id = phone_number_id or os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.recipient = recipient or os.getenv("WHATSAPP_RECIPIENT", "")
        self.timeout = timeout

    def send(self, message: str, payload: dict) -> dict:
        if not (self.token and self.phone_number_id and self.recipient):
            raise DeliveryError(
                "WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID / WHATSAPP_RECIPIENT eksik."
            )
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover
            raise DeliveryError("httpx kurulu değil.") from exc
        try:
            resp = httpx.post(
                f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": self.recipient,
                    "type": "text",
                    "text": {"body": message},
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            raise DeliveryError(f"WhatsApp gönderimi başarısız: {exc}") from exc
        return {"channel": self.channel, "status": "sent", "message": message}
