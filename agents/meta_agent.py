"""MetaAgent — Türkiye geneli konsolidasyon. STUB (adım 11).

11 depo raporunu birleştirir, executive summary üretir, öncelikli depo
sıralaması yapar. 1 depo raporu eksik olsa bile (çökmüş depo) diğerleriyle devam eder.
"""

from __future__ import annotations

from models.reports import DepotRiskReport, TurkeyWideReport


class MetaAgent:
    def consolidate(self, depot_reports: list[DepotRiskReport]) -> TurkeyWideReport:
        # TODO(adım 11): kritik/yüksek dağılımına göre depo önceliklendirme,
        # Claude API ile (fallback şablonla) Türkiye geneli özet.
        raise NotImplementedError("MetaAgent konsolidasyonu henüz uygulanmadı (adım 11).")
