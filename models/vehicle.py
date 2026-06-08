"""Araç modeli: Arvento'dan gelen anlık konum + sıcaklık + hareket verisi."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class VehicleReading(BaseModel):
    """Aracın bir andaki tam telemetrisi (konum + sıcaklık + hız)."""

    vehicle_id: str
    shipment_id: str | None = None
    depot_id: str | None = None

    lat: float | None = None
    lon: float | None = None
    temp_c: float | None = None
    speed_kmh: float | None = None

    measured_at: datetime = Field(default_factory=datetime.utcnow)
