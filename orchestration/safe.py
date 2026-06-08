"""Hata izolasyon yardımcısı — "pipeline durmamalı" kuralı.

Bir ajan çağrısı başarısız olursa fallback fonksiyonu çalışır; o da başarısız
olursa hata loglanır ve None döner. Hiçbir durumda istisna yukarı kaçmaz.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger("axiom.safe")

T = TypeVar("T")


def safe_run_agent(
    agent_fn: Callable[..., T],
    fallback_fn: Callable[..., T] | None = None,
    /,
    **kwargs,
) -> T | None:
    """`agent_fn`'i çağırır; hata olursa `fallback_fn`'e, o da olursa None'a düşer."""

    try:
        return agent_fn(**kwargs)
    except Exception as exc:  # noqa: BLE001 — pipeline'ı korumak için bilinçli geniş yakalama
        logger.warning("Ajan başarısız (%s); fallback deneniyor: %s", agent_fn, exc)

    if fallback_fn is None:
        return None

    try:
        return fallback_fn(**kwargs)
    except Exception as exc:  # noqa: BLE001
        logger.error("Fallback da başarısız (%s): %s", fallback_fn, exc)
        return None
