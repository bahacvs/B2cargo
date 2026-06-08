"""Rapor modelleri: depo bazlı ve Türkiye geneli."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from models.risk import RiskLevel, RiskResult
from models.signals import DataQualityAlert


class DepotRiskReport(BaseModel):
    """Tek bir deponun risk değerlendirme raporu (DepotAgent çıktısı)."""

    depot_id: str
    depot_name: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    results: list[RiskResult] = Field(default_factory=list)
    data_quality_alerts: list[DataQualityAlert] = Field(default_factory=list)

    # Alt ajan çıktıları (DepotAgent doldurur; üretilemezse boş kalır).
    explanation: str = ""
    actions: list[dict] = Field(default_factory=list)
    notifications: list[dict] = Field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for r in self.results if r.level is RiskLevel.CRITICAL)

    @property
    def max_score(self) -> float:
        return max((r.score for r in self.results), default=0.0)


class TurkeyWideReport(BaseModel):
    """MetaAgent çıktısı: 11 deponun konsolide Türkiye geneli raporu."""

    generated_at: datetime = Field(default_factory=datetime.utcnow)
    depot_reports: list[DepotRiskReport] = Field(default_factory=list)
    executive_summary: str = ""
    # Öncelikli depo sıralaması: en riskliden aza, depot_id listesi.
    prioritized_depots: list[str] = Field(default_factory=list)
