"""Adapter interface'leri (ABC).

Kritik kural: bu interface'ler DEĞİŞMEZ. Mock ve gerçek (prod) implementasyonlar
aynı imzaları paylaşır; çağıran kod hangisini kullandığını bilmez. Mock/prod seçimi
`adapters/factory.py` içinde `USE_MOCK_ADAPTERS` ortam değişkeniyle yapılır.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.stock import DepotSnapshot
from models.temperature import DepotZoneTemperature, VehicleTemperatureReading


class StockAdapter(ABC):
    """Stok / kalem / sevkiyat verisi kaynağı (Omnia veya Devambar).

    B2 Cargo Omnia'ya geçti: stok + sevkiyat verisi Omnia'dan gelir. Devambar
    artık yalnızca veritabanı (bağlantı sonra netleşecek). İki kaynak da bu
    interface'i implemente eder; çağıran kod hangisini kullandığını bilmez.
    """

    @abstractmethod
    def fetch_stock(self, depot_id: str) -> DepotSnapshot:
        """Verilen deponun anlık stok görüntüsünü döner."""


# Geriye dönük uyum: eski ad StockAdapter'a işaret eder.
DevambarAdapter = StockAdapter


class SensorAdapter(ABC):
    """Depo bölge (zon) sıcaklıkları (Sensor API)."""

    @abstractmethod
    def fetch_depot_temps(self, depot_id: str) -> list[DepotZoneTemperature]:
        """Deponun zon bazlı sıcaklık ölçümlerini döner."""


class ArventoAdapter(ABC):
    """Araç anlık konum + araç içi sıcaklık (Arvento API)."""

    @abstractmethod
    def fetch_vehicle_temps(self, depot_id: str) -> list[VehicleTemperatureReading]:
        """Depoya bağlı sevkiyatlardaki araç sıcaklık okumalarını döner."""
