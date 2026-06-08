"""Ara sinyaller — TemperatureMonitorAgent çıktısı, StockRiskAgent girdisi.

Bu sinyaller ham veri ile risk skoru arasındaki köprüdür. Kalemler arası akış:
TemperatureMonitor → (TemperatureDeviation, DataQualityAlert) → StockRisk.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class DeviationSource(str, Enum):
    """Sapmanın hangi sıcaklık boyutundan geldiği."""

    DEPOT_ZONE = "DEPOT_ZONE"  # Sensor → depo zonu
    VEHICLE = "VEHICLE"  # Arvento → araç içi


class DeviationDirection(str, Enum):
    BELOW_MIN = "BELOW_MIN"
    ABOVE_MAX = "ABOVE_MAX"


class TemperatureDeviation(BaseModel):
    """Bir kalemin izin verilen aralık dışına çıkmış sıcaklık sapması."""

    item_id: str
    depot_id: str
    source: DeviationSource
    direction: DeviationDirection
    measured_c: float
    limit_c: float  # aşılan sınır (min ya da max)
    magnitude_c: float  # sınırdan sapma büyüklüğü (mutlak)


class DataQualityAlert(BaseModel):
    """Veri eksikliği/kalitesizliği — pipeline durmaz, kayıt altına alınır.

    Örn: kalem sıcaklık izlemesi gerektiriyor ama ölçüm gelmedi/null.
    """

    depot_id: str
    item_id: str | None = None
    code: str
    message: str
    context: dict = Field(default_factory=dict)
