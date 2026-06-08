"""Günlük 07:00 pipeline. STUB (adım 12 ile bağlanır).

Akış (CLAUDE.md):
  fetch_all_depots → her depo için:
    fetch_stock(Devambar) / fetch_depot_temps(Sensor) / fetch_vehicle_temps(Arvento)
    run_depot_agent(snapshot)   # safe_run_agent ile sarılı, 1 depo çökerse diğerleri devam
  → meta_agent.consolidate(all_depot_reports)
  → send_daily_report

Adapter seçimi adapters.factory üzerinden (USE_MOCK_ADAPTERS).
"""

from __future__ import annotations

from models.reports import TurkeyWideReport


def run_daily_pipeline() -> TurkeyWideReport:
    # TODO(adım 12): factory'den adapter'ları al, tüm depoları işle, MetaAgent ile konsolide et.
    raise NotImplementedError("Günlük pipeline henüz uygulanmadı (adım 12).")
