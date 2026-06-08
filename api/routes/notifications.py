"""Bildirim endpoint'leri. Adım 13.

GET /notifications        → tüm depoların bekleyen bildirim payload'ları
POST /notifications/alert → anlık alarm: {"depot_id": "..."} → bildirimler
"""

from __future__ import annotations

from fastapi import APIRouter

from orchestration.alert_pipeline import run_alert_pipeline
from orchestration.daily_pipeline import run_daily_pipeline

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications() -> list[dict]:
    report = run_daily_pipeline()
    payloads: list[dict] = []
    for depot in report.depot_reports:
        payloads.extend(depot.notifications)
    return payloads


@router.post("/alert")
def trigger_alert(event: dict) -> list[dict]:
    return run_alert_pipeline(event)
