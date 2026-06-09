"""Statik (sunucusuz) dashboard prototipi üretir.

run_daily_pipeline()'ın mock çıktısını dashboard/index.html içine gömerek tek
dosyalık, çevrimdışı açılabilen bir HTML üretir. Tarayıcıda doğrudan açılır;
FastAPI/uvicorn gerekmez.

Çalıştırma:
    USE_MOCK_ADAPTERS=true python scripts/build_static_dashboard.py [çıktı.html]
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("USE_MOCK_ADAPTERS", "true")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from orchestration.daily_pipeline import run_daily_pipeline  # noqa: E402

# Panelin canlıda fetch ettiği satırları gömülü veriyle değiştir.
_FETCH_SNIPPET = '''    const resp = await fetch("/reports/turkey");
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const data = await resp.json();'''
_EMBED_SNIPPET = "    const data = window.__EMBEDDED__;"


def build(output: Path) -> Path:
    report = run_daily_pipeline()
    data_json = json.dumps(report.model_dump(mode="json"), ensure_ascii=False)

    html = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    if _FETCH_SNIPPET not in html:
        raise SystemExit("dashboard/index.html fetch bloğu bulunamadı — şablon değişmiş.")

    html = html.replace(_FETCH_SNIPPET, _EMBED_SNIPPET)
    inject = f"<script>window.__EMBEDDED__ = {data_json};</script>\n<script>"
    html = html.replace("<script>", inject, 1)
    # Başlığa "prototip / örnek veri" notu ekle.
    html = html.replace(
        'B2 Cargo — Türkiye Geneli Lojistik Risk Paneli',
        'B2 Cargo — Türkiye Geneli Lojistik Risk Paneli · PROTOTİP (örnek veri)',
    )

    output.write_text(html, encoding="utf-8")
    return output


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dashboard" / "prototype.html"
    path = build(out)
    print(f"Statik prototip üretildi: {path}")
