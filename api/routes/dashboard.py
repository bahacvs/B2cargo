"""Dashboard endpoint — tek dosyalık izleme paneli.

GET /        → dashboard HTML (tarayıcıda görsel izleme)
Panel, /reports/turkey JSON endpoint'ini fetch ederek depo önceliklerini, kalem
risklerini, açıklama/aksiyon/bildirimleri görselleştirir. Build/CDN gerektirmez.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])

_DASHBOARD_HTML = (
    Path(__file__).resolve().parent.parent.parent / "dashboard" / "index.html"
)


@router.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return _DASHBOARD_HTML.read_text(encoding="utf-8")
