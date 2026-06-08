"""Rapor endpoint'leri. Adım 13.

GET /reports/turkey      → Türkiye geneli TurkeyWideReport (tüm depolar)
GET /reports/{depot_id}  → tek deponun DepotRiskReport'u

Şimdilik istek anında pipeline'ı çalıştırır (mock adapter'larla hızlı). İleride
DB'den/cache'ten okunacak (pipeline_runs / risk_assessments).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from config import all_depot_ids
from models.reports import DepotRiskReport, TurkeyWideReport
from orchestration.daily_pipeline import run_daily_pipeline

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/turkey", response_model=TurkeyWideReport)
def get_turkey_report() -> TurkeyWideReport:
    return run_daily_pipeline()


@router.get("/{depot_id}", response_model=DepotRiskReport)
def get_depot_report(depot_id: str) -> DepotRiskReport:
    if depot_id not in all_depot_ids():
        raise HTTPException(status_code=404, detail=f"Bilinmeyen depo: {depot_id}")
    report = run_daily_pipeline(depot_ids=[depot_id])
    if not report.depot_reports:
        # Devambar erişilemedi → depo atlandı.
        raise HTTPException(status_code=503, detail=f"Depo verisi alınamadı: {depot_id}")
    return report.depot_reports[0]
