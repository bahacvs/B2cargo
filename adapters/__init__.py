"""Veri kaynağı adapter'ları.

Stok/sevkiyat kaynağı: Omnia (ana) veya Devambar (DB, sonra netleşecek).
Sıcaklık: Sensor (depo zonu), Arvento (araç). Her kaynağın Mock + gerçek
implementasyonu vardır; seçim adapters.factory üzerinden yapılır.
"""

from adapters.base import (
    ArventoAdapter,
    DevambarAdapter,
    SensorAdapter,
    StockAdapter,
)
from adapters.errors import AdapterError

__all__ = [
    "StockAdapter",
    "DevambarAdapter",
    "SensorAdapter",
    "ArventoAdapter",
    "AdapterError",
]
