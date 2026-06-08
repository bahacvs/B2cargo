"""Sıcaklık modelleri: iki boyut.

Araç sıcaklığı  → Arvento → VehicleTemperatureReading (sevkiyat boyunca)
Depo sıcaklığı  → Sensor  → DepotZoneTemperature (zon bazında)
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DepotZoneTemperature(BaseModel):
    """Bir depo zonunun (bölgesinin) anlık sıcaklığı — Sensor API."""

    depot_id: str
    zone_id: str
    temp_c: float
    measured_at: datetime = Field(default_factory=datetime.utcnow)


class VehicleTemperatureReading(BaseModel):
    """Sevkiyat sırasında araç içi sıcaklık — Arvento API."""

    vehicle_id: str
    shipment_id: str | None = None
    temp_c: float
    measured_at: datetime = Field(default_factory=datetime.utcnow)
