"""Anlık alarm pipeline (event-driven).

Akış (CLAUDE.md):
  temperature_event_received → check_threshold
  → if alert: run_alert_pipeline → build_notification_payload

Pratik uygulama: bir sıcaklık olayı geldiğinde ilgili deponun güncel verisi
çekilir, DepotAgent çalıştırılır ve KRİTİK/YÜKSEK kalemler için bildirim
payload'ları döner. Eşikler risk_weights.yaml'dan (deterministik).
"""

from __future__ import annotations

from adapters.factory import (
    get_arvento_adapter,
    get_devambar_adapter,
    get_sensor_adapter,
)
from orchestration.daily_pipeline import _run_one_depot
from config import load_depots


def run_alert_pipeline(event: dict) -> list[dict]:
    """`event["depot_id"]` deposunu değerlendirip bildirim payload'ları döner."""

    depot_id = event["depot_id"]
    report = _run_one_depot(
        depot_id,
        load_depots(),
        get_devambar_adapter(),
        get_sensor_adapter(),
        get_arvento_adapter(),
    )
    if report is None:
        return []
    return report.notifications
