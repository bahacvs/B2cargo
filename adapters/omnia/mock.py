"""MockOmniaAdapter — Omnia'dan stok + sevkiyat verisi (gerçek API olmadan).

Omnia artık ana veri kaynağı (stok + sevkiyat). Mock, mock_data/depots/<id>_stock.json
dosyalarından okur (Devambar mock'u ile aynı şema; veri kaynağı değişti, model değil).
`fail_depots` ile API çökmesi simüle edilir → "kaynak cevap vermezse depot skip".
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from adapters._mock_loader import DEFAULT_DATA_DIR, load_json
from adapters.base import StockAdapter
from adapters.errors import AdapterError
from models.stock import DepotSnapshot, StockItem


class MockOmniaAdapter(StockAdapter):
    def __init__(
        self,
        snapshots: dict[str, DepotSnapshot] | None = None,
        data_dir: str | Path = DEFAULT_DATA_DIR,
        fail_depots: Iterable[str] | None = None,
    ) -> None:
        self._snapshots = snapshots or {}
        self._data_dir = Path(data_dir)
        self._fail_depots = set(fail_depots or [])

    def fetch_stock(self, depot_id: str) -> DepotSnapshot:
        if depot_id in self._fail_depots:
            raise AdapterError(f"Omnia API erişilemedi: {depot_id}")

        if depot_id in self._snapshots:
            return self._snapshots[depot_id]

        raw = load_json(self._data_dir, depot_id, "stock")
        items = [StockItem(**row) for row in (raw or [])]
        return DepotSnapshot(depot_id=depot_id, items=items)
