"""Stok modelleri: Devambar kaynaklı kalem ve depo snapshot'ı.

`needs_temp_monitoring` tüm sistemde sıcaklık izleme kapısının TEK otoritesidir;
TemperatureMonitorAgent ve StockRiskAgent bu fonksiyonu import eder (kural tekrarı yok).
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class StockItem(BaseModel):
    """Devambar'dan gelen tek bir stok kalemi.

    `temp_min_c` / `temp_max_c` null ise ürün sıcaklık izlemesi gerektirmez
    (kuru gıda, ambalajlı ürün vb.). Kategori config'de tanımlanmaz —
    Devambar bu bilgiyi zaten gönderir.
    """

    item_id: str
    sku: str | None = None
    name: str
    category: str | None = None
    quantity: float = 0.0
    unit: str | None = None

    # Sıcaklık aralığı — null ise izlenmez.
    temp_min_c: float | None = None
    temp_max_c: float | None = None

    # Konum eşleştirmesi: kalem hangi depoda, hangi zonda.
    depot_id: str
    zone_id: str | None = None

    # Sevkiyat bağlamı (yolda olan kalemler için).
    shipment_id: str | None = None
    vehicle_id: str | None = None

    expiry_date: date | None = None


class DepotSnapshot(BaseModel):
    """Bir deponun belirli bir andaki stok görüntüsü."""

    depot_id: str
    taken_at: datetime = Field(default_factory=datetime.utcnow)
    items: list[StockItem] = Field(default_factory=list)


def needs_temp_monitoring(item: StockItem) -> bool:
    """Kalemin sıcaklık izlemesi gerekip gerekmediğini söyler.

    Devambar `temp_min_c` ve `temp_max_c` doluysa izlenir; null ise atlanır.
    Bu fonksiyon sistemdeki TEK sıcaklık-izleme kuralıdır.
    """

    return item.temp_min_c is not None and item.temp_max_c is not None
