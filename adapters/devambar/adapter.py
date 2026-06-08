"""DevambarApiAdapter — gerçek (prod) implementasyon, STUB (adım 14).

Mock ile AYNI interface (DevambarAdapter). Client'ten gelen ham JSON'u
StockItem/DepotSnapshot'a çevirecek. İmza dışında hiçbir çağıran kod değişmez.
"""

from __future__ import annotations

from adapters.base import DevambarAdapter
from adapters.devambar.client import DevambarClient
from models.stock import DepotSnapshot


class DevambarApiAdapter(DevambarAdapter):
    def __init__(self, client: DevambarClient | None = None) -> None:
        self._client = client or DevambarClient()

    def fetch_stock(self, depot_id: str) -> DepotSnapshot:
        # TODO(adım 14): self._client.get_stock(depot_id) → StockItem listesine map et.
        raise NotImplementedError(
            "Devambar gerçek adapter henüz uygulanmadı (adım 14). "
            "Geliştirmede MockDevambarAdapter kullanın."
        )
