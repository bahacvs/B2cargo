"""Bildirim kanalı factory — mock/gerçek seçimi tek yerde.

USE_MOCK_NOTIFIERS (varsayılan true): tüm kanallar MockNotifier (gönderim simüle).
false: whatsapp→WhatsAppNotifier, telegram→TelegramNotifier, dashboard→NullNotifier.
Aciliyet→kanal eşlemesi notification_rules.json'da; burada sadece kanal→gönderici.
"""

from __future__ import annotations

import os

from delivery.base import NullNotifier
from delivery.dispatcher import NotificationDispatcher
from delivery.mock import MockNotifier
from delivery.telegram import TelegramNotifier
from delivery.whatsapp import WhatsAppNotifier


def _use_mock() -> bool:
    return os.getenv("USE_MOCK_NOTIFIERS", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_dispatcher() -> NotificationDispatcher:
    if _use_mock():
        return NotificationDispatcher(
            {
                "whatsapp": MockNotifier("whatsapp"),
                "telegram": MockNotifier("telegram"),
                "dashboard": NullNotifier("dashboard"),
            }
        )
    return NotificationDispatcher(
        {
            "whatsapp": WhatsAppNotifier(),
            "telegram": TelegramNotifier(),
            "dashboard": NullNotifier("dashboard"),
        }
    )
