"""Bildirim teslim katmanı: WhatsApp / Telegram kanalları + dispatcher.

NotificationBuilder payload üretir (kanal = aciliyet skoru); bu katman gönderir.
"""

from delivery.dispatcher import (
    NotificationDispatcher,
    dispatch_report,
    dispatch_turkey,
    format_message,
)
from delivery.errors import DeliveryError
from delivery.factory import get_dispatcher
from delivery.mock import MockNotifier

__all__ = [
    "NotificationDispatcher",
    "dispatch_report",
    "dispatch_turkey",
    "format_message",
    "get_dispatcher",
    "MockNotifier",
    "DeliveryError",
]
