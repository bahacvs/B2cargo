"""Health endpoint mantığı — framework'ten bağımsız, şimdiden çalışır.

API katmanı (adım 13) bunu bir route'a bağlayacak. Saf fonksiyon olduğu için
deterministik çekirdekte test edilebilir.
"""

from __future__ import annotations

import os


def health_status() -> dict:
    """Servisin temel sağlık bilgisini döner."""

    return {
        "status": "ok",
        "service": "axiom-logistics-intelligence",
        "use_mock_adapters": os.getenv("USE_MOCK_ADAPTERS", "true"),
    }
