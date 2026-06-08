"""Health endpoint. Adım 13.

`health_status()` framework'ten bağımsız saf fonksiyon (deterministik çekirdekte
test edilir); `router` FastAPI'ye bağlar.
"""

from __future__ import annotations

import os

from fastapi import APIRouter

router = APIRouter(tags=["health"])


def health_status() -> dict:
    """Servisin temel sağlık bilgisini döner."""

    return {
        "status": "ok",
        "service": "axiom-logistics-intelligence",
        "use_mock_adapters": os.getenv("USE_MOCK_ADAPTERS", "true"),
    }


@router.get("/health")
def get_health() -> dict:
    return health_status()
