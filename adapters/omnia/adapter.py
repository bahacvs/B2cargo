"""OmniaApiAdapter — gerçek (prod) implementasyon.

Mock ile AYNI interface (StockAdapter). Omnia alan adları modelden farklıysa
eşleme burada yapılır; varsayılan eşleme model alan adlarıyla aynıdır.
Gerçek Omnia şeması netleştiğinde _FIELD_MAP genişletilir.
"""

from __future__ import annotations

from adapters.base import StockAdapter
from adapters.omnia.client import OmniaClient
from models.stock import DepotSnapshot, StockItem

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


class OmniaApiAdapter(StockAdapter):
    def __init__(self, client: OmniaClient | None = None) -> None:
        self._client = client or OmniaClient()

    def fetch_stock(self, depot_id: str) -> DepotSnapshot:
        rows = self._client.get_stock(depot_id)
        items = [self._to_item(depot_id, row) for row in rows]
        return DepotSnapshot(depot_id=depot_id, items=items)

    @staticmethod
    def _to_item(depot_id: str, row: dict) -> StockItem:
        mapped = {
            field: row[src]
            for src, field in _FIELD_MAP.items()
            if src in row and row[src] is not None
        }
        mapped["depot_id"] = depot_id
        return StockItem(**mapped)
