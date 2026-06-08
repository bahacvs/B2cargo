"""Rapor endpoint'leri — STUB (adım 13).

GET /reports/turkey      → en güncel TurkeyWideReport
GET /reports/{depot_id}  → depo bazlı DepotRiskReport
"""

from __future__ import annotations


def get_turkey_report() -> dict:
    # TODO(adım 13): en güncel TurkeyWideReport'u DB'den/cache'ten döndür.
    raise NotImplementedError("Rapor endpoint'i henüz uygulanmadı (adım 13).")


def get_depot_report(depot_id: str) -> dict:
    # TODO(adım 13).
    raise NotImplementedError("Depo rapor endpoint'i henüz uygulanmadı (adım 13).")
