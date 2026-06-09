"""Omnia HTTP client (httpx). Gerçek bağlantı detayı geldiğinde tamamlanır.

OMNIA_API_URL / OMNIA_API_KEY ile konuşur. httpx lazy import edilir; HTTP/ağ
hatası AdapterError'a çevrilir (pipeline izolasyonu).
"""

from __future__ import annotations

import os

from adapters.errors import AdapterError


class OmniaClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("OMNIA_API_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("OMNIA_API_KEY", "")
        self.timeout = timeout

    def get_stock(self, depot_id: str) -> list[dict]:
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover
            raise AdapterError("httpx kurulu değil.") from exc
        if not self.base_url:
            raise AdapterError("OMNIA_API_URL tanımlı değil.")
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            resp = httpx.get(
                f"{self.base_url}/stock",
                params={"depot_id": depot_id},
                headers=headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            raise AdapterError(f"Omnia isteği başarısız: {exc}") from exc
        return data.get("items", data) if isinstance(data, dict) else data
