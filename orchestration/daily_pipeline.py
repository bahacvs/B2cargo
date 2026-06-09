"""Günlük 07:00 pipeline (config-driven, hata izole). Adım 12 ile zamanlanır.

Akış (CLAUDE.md):
  her depo için: fetch_stock(Devambar) / fetch_depot_temps(Sensor) /
  fetch_vehicle_temps(Arvento) → DepotAgent.run → DepotRiskReport
  → MetaAgent.consolidate → TurkeyWideReport

Hata izolasyonu:
  - Devambar erişilemezse o depo atlanır, diğer depolar devam (depot skip).
  - Sensor/Arvento erişilemezse o sinyal boş geçilir (fallback), depo yine işlenir.
  - DepotAgent içindeki AI alt-ajanları zaten safe_run_agent ile sarılı.

Adapter seçimi adapters.factory üzerinden (USE_MOCK_ADAPTERS).
"""

from __future__ import annotations

import logging

from adapters.base import ArventoAdapter, SensorAdapter, StockAdapter
from adapters.errors import AdapterError
from adapters.factory import (
    get_arvento_adapter,
    get_sensor_adapter,
    get_stock_adapter,
)
from agents.depot_agent import DepotAgent
from agents.meta_agent import MetaAgent
from config import all_depot_ids, load_depots
from models.reports import DepotRiskReport, TurkeyWideReport

logger = logging.getLogger("axiom.pipeline")


def run_daily_pipeline(
    depot_ids: list[str] | None = None,
    *,
    stock: StockAdapter | None = None,
    sensor: SensorAdapter | None = None,
    arvento: ArventoAdapter | None = None,
    meta_agent: MetaAgent | None = None,
) -> TurkeyWideReport:
    stock = stock or get_stock_adapter()
    sensor = sensor or get_sensor_adapter()
    arvento = arvento or get_arvento_adapter()
    meta_agent = meta_agent or MetaAgent()

    depots = load_depots()
    ids = depot_ids or all_depot_ids()

    reports: list[DepotRiskReport] = []
    for depot_id in ids:
        report = _run_one_depot(depot_id, depots, stock, sensor, arvento)
        if report is not None:
            reports.append(report)

    return meta_agent.consolidate(reports)


def _run_one_depot(
    depot_id: str,
    depots: dict[str, dict],
    stock: StockAdapter,
    sensor: SensorAdapter,
    arvento: ArventoAdapter,
) -> DepotRiskReport | None:
    # Stok kaynağı (Omnia) zorunlu: erişilemezse depo atlanır (diğerleri devam).
    try:
        snapshot = stock.fetch_stock(depot_id)
    except AdapterError as exc:
        logger.warning("Omnia erişilemedi, depo atlandı (%s): %s", depot_id, exc)
        return None

    # Sensor / Arvento opsiyonel: erişilemezse boş geçilir (fallback).
    depot_temps = _safe_fetch(sensor.fetch_depot_temps, depot_id, "Sensor")
    vehicle_temps = _safe_fetch(arvento.fetch_vehicle_temps, depot_id, "Arvento")

    config = depots.get(depot_id, {"id": depot_id})
    agent = DepotAgent(config=config)
    return agent.run(
        snapshot, depot_temps=depot_temps, vehicle_temps=vehicle_temps
    )


def _safe_fetch(fetch_fn, depot_id: str, source: str) -> list:
    try:
        return fetch_fn(depot_id)
    except AdapterError as exc:
        logger.warning("%s erişilemedi, boş geçildi (%s): %s", source, depot_id, exc)
        return []
