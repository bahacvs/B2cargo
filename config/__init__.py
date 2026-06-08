"""Config yükleyiciler — YAML/JSON dosyalarını tek yerden okur.

Depo ve risk ağırlıkları kodda değil bu klasördeki dosyalarda yaşar.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def load_depots() -> dict[str, dict]:
    """depots.yaml → {depot_id: depot_config}."""

    with (CONFIG_DIR / "depots.yaml").open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return {d["id"]: d for d in data.get("depots", [])}


def all_depot_ids() -> list[str]:
    """Tanımlı tüm depo id'leri (11 ajan = 1 kod örnekleme için)."""

    return list(load_depots().keys())


@lru_cache(maxsize=1)
def load_risk_weights() -> dict:
    """risk_weights.yaml → eşikler + gerekçe ağırlıkları."""

    with (CONFIG_DIR / "risk_weights.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=1)
def load_notification_rules() -> dict:
    """notification_rules.json → bildirim kuralları."""

    with (CONFIG_DIR / "notification_rules.json").open(encoding="utf-8") as fh:
        return json.load(fh)
