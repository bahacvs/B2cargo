"""Bildirim teslim katmanı testleri (WhatsApp/Telegram, aciliyet bazlı)."""

from __future__ import annotations

import pytest

from delivery.base import NullNotifier
from delivery.dispatcher import NotificationDispatcher, format_message
from delivery.errors import DeliveryError
from delivery.mock import MockNotifier
from models.reports import DepotRiskReport


def _dispatcher():
    return NotificationDispatcher(
        {
            "whatsapp": MockNotifier("whatsapp"),
            "telegram": MockNotifier("telegram"),
            "dashboard": NullNotifier("dashboard"),
        }
    )


def test_format_message_turkish():
    msg = format_message(
        {"depot_id": "ankara", "item_id": "x", "level": "CRITICAL", "score": 95,
         "reasons": ["temp_deviation_depot"]}
    )
    assert "KRİTİK" in msg and "ankara" in msg and "95" in msg


def test_routes_payload_to_correct_channel():
    d = _dispatcher()
    payloads = [
        {"channel": "whatsapp", "item_id": "a", "level": "CRITICAL", "score": 95, "reasons": []},
        {"channel": "telegram", "item_id": "a", "level": "CRITICAL", "score": 95, "reasons": []},
    ]
    results = d.dispatch(payloads)
    assert {r["channel"] for r in results} == {"whatsapp", "telegram"}
    assert all(r["status"] == "sent" for r in results)


def test_unknown_channel_skipped():
    d = NotificationDispatcher({"telegram": MockNotifier("telegram")})
    results = d.dispatch([{"channel": "sms", "item_id": "a", "score": 1, "reasons": []}])
    assert results == []


def test_one_channel_failure_isolated():
    class Boom(MockNotifier):
        def send(self, message, payload):
            raise DeliveryError("patladı")

    d = NotificationDispatcher({"whatsapp": Boom("whatsapp"), "telegram": MockNotifier("telegram")})
    payloads = [
        {"channel": "whatsapp", "item_id": "a", "level": "CRITICAL", "score": 9, "reasons": []},
        {"channel": "telegram", "item_id": "a", "level": "CRITICAL", "score": 9, "reasons": []},
    ]
    results = d.dispatch(payloads)
    statuses = {r["channel"]: r["status"] for r in results}
    assert statuses["whatsapp"] == "failed"
    assert statuses["telegram"] == "sent"  # diğer kanal etkilenmez


def test_dispatch_report_sends_critical_via_whatsapp_and_telegram():
    # notification_rules.json: CRITICAL → [whatsapp, telegram]
    from agents.sub_agents.notification_builder import NotificationBuilder
    from models.risk import RiskLevel, RiskResult

    result = RiskResult(item_id="ank-frozen-001", depot_id="ankara", score=95,
                        level=RiskLevel.CRITICAL)
    report = DepotRiskReport(depot_id="ankara", results=[result])
    report.notifications = NotificationBuilder().build(report)

    d = _dispatcher()
    d.dispatch(report.notifications)
    wa = d._notifiers["whatsapp"].sent
    tg = d._notifiers["telegram"].sent
    assert any(m["item_id"] == "ank-frozen-001" for m in wa)
    assert any(m["item_id"] == "ank-frozen-001" for m in tg)
