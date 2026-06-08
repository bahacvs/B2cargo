"""FastAPI uygulama girişi. Adım 13.

create_app() → reports / notifications / health router'larını birleştirir.
Çalıştırma: uvicorn api.main:app --reload  (app = create_app()).
"""

from __future__ import annotations

from fastapi import FastAPI

from api.routes import dashboard, health, notifications, reports


def create_app() -> FastAPI:
    app = FastAPI(
        title="Axiom Logistics Intelligence",
        description="B2 Cargo çok-ajanlı lojistik zekâ sistemi API'si.",
        version="0.1.0",
    )
    app.include_router(dashboard.router)
    app.include_router(health.router)
    app.include_router(reports.router)
    app.include_router(notifications.router)
    return app


app = create_app()
