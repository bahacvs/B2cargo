"""Arvento HTTP client — STUB (adım 14)."""

from __future__ import annotations

import os


class ArventoClient:
    def __init__(
        self, base_url: str | None = None, api_key: str | None = None
    ) -> None:
        self.base_url = base_url or os.getenv("ARVENTO_API_URL", "")
        self.api_key = api_key or os.getenv("ARVENTO_API_KEY", "")

    def get_vehicle_temps(self, depot_id: str) -> list[dict]:
        # TODO(adım 14): httpx ile araç konum + sıcaklık verisini çek.
        raise NotImplementedError("Arvento gerçek client henüz uygulanmadı (adım 14).")
