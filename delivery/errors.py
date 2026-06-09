"""Teslim (bildirim gönderme) hata tipi."""

from __future__ import annotations


class DeliveryError(RuntimeError):
    """Bir bildirim kanalına (WhatsApp/Telegram) gönderim başarısız olduğunda."""
