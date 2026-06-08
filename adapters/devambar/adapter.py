"""DevambarApiAdapter — gerçek (prod) implementasyon. Adım 14.

Mock ile AYNI interface (DevambarAdapter). Ham JSON'u StockItem/DepotSnapshot'a
çevirir. Devambar alan adları bizim modelden farklıysa eşleme burada yapılır;
varsayılan eşleme model alan adlarıyla aynıdır, eksikler güvenle atlanır.
"""

from __future__ import annotations

from adapters.base import DevambarAdapter
from adapters.devambar.client import DevambarClient
from models.stock import DepotSnapshot, StockItem

# Devambar alanı → model alanı (gerçek API şeması geldikçe genişletilir).
_FIELD_MAP = {
    "item_id": "item_id",
    "sku": "sku",
    "name": "name",
    "category": "category",
    "quantity": "quantity",
    "unit": "unit",
    "temp_min_c": "temp_min_c",
    "temp_max_c": "temp_max_c",
    "zone_id": "zone_id",
    "shipment_id": "shipment_id",
    "vehicle_id": "vehicle_id",
    "expiry_date": "expiry_date",
}


class DevambarApiAdapter(DevambarAdapter):
    def __init__(self, client: DevambarClient | None = None) -> None:
        self._client = client or DevambarClient()

    def fetch_stock(self, depot_id: str) -> DepotSnapshot:
        rows = self._client.get_stock(depot_id)
        items = [self._to_item(depot_id, row) for row in rows]
        return DepotSnapshot(depot_id=depot_id, items=items)

    @staticmethod
    def _to_item(depot_id: str, row: dict) -> StockItem:
        mapped = {
            model_field: row[src]
            for src, model_field in _FIELD_MAP.items()
            if src in row and row[src] is not None
        }
        mapped["depot_id"] = depot_id
        return StockItem(**mapped)
