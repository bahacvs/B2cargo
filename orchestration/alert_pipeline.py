"""Anlık alarm pipeline (event-driven). STUB.

Akış (CLAUDE.md):
  temperature_event_received → check_threshold
  → if alert: run_alert_pipeline → build_notification_payload
"""

from __future__ import annotations


def run_alert_pipeline(event: dict) -> list[dict]:
    # TODO: eşik kontrolü → alarm ise risk değerlendir → NotificationBuilder payload.
    raise NotImplementedError("Alarm pipeline henüz uygulanmadı.")
