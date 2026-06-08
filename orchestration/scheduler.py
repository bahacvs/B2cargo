"""APScheduler kurulumu — 07:00 günlük cron. Adım 12.

TIMEZONE ortam değişkenine (Europe/Istanbul) göre run_daily_pipeline'ı tetikler.
apscheduler bağımlılığı opsiyonel: yoksa modül import edilebilir, start_scheduler
çağrısında net hata verir.
"""

from __future__ import annotations

import logging
import os

from orchestration.daily_pipeline import run_daily_pipeline

logger = logging.getLogger("axiom.scheduler")


def _run_daily_job() -> None:
    """Cron tetikleyicisinin çağırdığı iş — hata loglanır, scheduler düşmez."""

    try:
        report = run_daily_pipeline()
        logger.info(
            "Günlük pipeline tamam: %d depo, öncelik: %s",
            len(report.depot_reports),
            report.prioritized_depots[:3],
        )
    except Exception:  # noqa: BLE001 - scheduler thread'i korunur
        logger.exception("Günlük pipeline başarısız")


def create_scheduler(hour: int = 7, minute: int = 0):
    """BackgroundScheduler oluşturur ve 07:00 cron job'ını ekler (başlatmaz)."""

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError as exc:  # pragma: no cover - ortam bağımlı
        raise RuntimeError(
            "apscheduler kurulu değil. requirements.txt'te aktif edin (adım 12)."
        ) from exc

    timezone = os.getenv("TIMEZONE", "Europe/Istanbul")
    scheduler = BackgroundScheduler(timezone=timezone)
    scheduler.add_job(
        _run_daily_job,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
        id="daily_report",
        replace_existing=True,
    )
    return scheduler


def start_scheduler():
    """Scheduler'ı oluşturup başlatır ve döner (uygulama yaşam döngüsünde tutulur)."""

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler başlatıldı (07:00 %s).", os.getenv("TIMEZONE", "Europe/Istanbul"))
    return scheduler
