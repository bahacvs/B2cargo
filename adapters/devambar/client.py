"""Devambar HTTP client — STUB (adım 14: gerçek API geldiğinde).

DEVAMBAR_API_URL / DEVAMBAR_API_KEY ile konuşacak. Şimdilik iskelet.
"""

from __future__ import annotations

import os


class DevambarClient:
    def __init__(
        self, base_url: str | None = None, api_key: str | None = None
    ) -> None:
        self.base_url = base_url or os.getenv("DEVAMBAR_API_URL", "")
        self.api_key = api_key or os.getenv("DEVAMBAR_API_KEY", "")

    def get_stock(self, depot_id: str) -> list[dict]:
        # TODO(adım 14): httpx ile GET /stock?depot=... çağrısı, JSON döndür.
        raise NotImplementedError("Devambar gerçek client henüz uygulanmadı (adım 14).")
