"""Mock adapter'lar için ortak JSON yükleyici.

`mock_data/depots/<depot_id>_<kind>.json` dosyalarını okur. Dosya yoksa boş döner;
böylece eksik veri kaynağı, çökme değil, "veri yok" olarak ele alınır.
"""

from __future__ import annotations

import json
from pathlib import Path

# Repo kökü → mock_data/depots
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "mock_data" / "depots"


def load_json(data_dir: Path, depot_id: str, kind: str) -> list | dict | None:
    """`<depot_id>_<kind>.json` içeriğini döner; dosya yoksa None."""

    path = Path(data_dir) / f"{depot_id}_{kind}.json"
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)
