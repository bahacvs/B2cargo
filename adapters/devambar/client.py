"""Devambar HTTP client (httpx). Adım 14.

DEVAMBAR_API_URL / DEVAMBAR_API_KEY ile konuşur. httpx opsiyonel bağımlılıktır;
import-safe kalması için lazy import edilir. HTTP/ağ hatası AdapterError'a çevrilir.
"""

from __future__ import annotations

import os

from adapters.errors import AdapterError


class DevambarClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("DEVAMBAR_API_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("DEVAMBAR_API_KEY", "")
        self.timeout = timeout

    def _get(self, path: str, params: dict) -> dict:
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover
            raise AdapterError("httpx kurulu değil (gerçek adapter için gerekli).") from exc
        if not self.base_url:
            raise AdapterError("DEVAMBAR_API_URL tanımlı değil.")
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            resp = httpx.get(
                f"{self.base_url}{path}",
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001 - tek tip AdapterError
            raise AdapterError(f"Devambar isteği başarısız: {exc}") from exc

    def get_stock(self, depot_id: str) -> list[dict]:
        """Deponun stok kalemlerini ham JSON satırları olarak döner."""

        data = self._get("/stock", {"depot_id": depot_id})
        # Devambar yanıtı: {"items": [...]} bekleniyor; düz liste de tolere edilir.
        return data.get("items", data) if isinstance(data, dict) else data
