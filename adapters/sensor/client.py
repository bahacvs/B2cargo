"""Sensor HTTP client (httpx). Adım 14."""

from __future__ import annotations

import os

from adapters.errors import AdapterError


class SensorClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("SENSOR_API_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("SENSOR_API_KEY", "")
        self.timeout = timeout

    def get_depot_temps(self, depot_id: str) -> list[dict]:
        try:
            import httpx
        except ImportError as exc:  # pragma: no cover
            raise AdapterError("httpx kurulu değil.") from exc
        if not self.base_url:
            raise AdapterError("SENSOR_API_URL tanımlı değil.")
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            resp = httpx.get(
                f"{self.base_url}/zones",
                params={"depot_id": depot_id},
                headers=headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            raise AdapterError(f"Sensor isteği başarısız: {exc}") from exc
        return data.get("zones", data) if isinstance(data, dict) else data
