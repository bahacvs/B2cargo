"""MetaAgent — Türkiye geneli konsolidasyon. Adım 11.

Deterministik kısım: depo önceliklendirme (kritik sayısı, sonra en yüksek skor).
AI kısım: Claude ile Türkçe executive summary; başarısızsa template fallback.
Eksik (çökmüş) depo raporu olsa bile diğerleriyle devam eder.
"""

from __future__ import annotations

from agents.llm import ClaudeClient
from models.reports import DepotRiskReport, TurkeyWideReport
from orchestration.safe import safe_run_agent


def _priority_key(report: DepotRiskReport) -> tuple:
    # En riskli önce: çok kritik kalem, sonra en yüksek skor.
    return (report.critical_count, report.max_score)


class _TemplateMetaSummary:
    """AI olmadan deterministik Türkiye geneli özet."""

    def generate(self, depot_reports: list[DepotRiskReport]) -> str:
        toplam_depo = len(depot_reports)
        toplam_kritik = sum(r.critical_count for r in depot_reports)
        sirali = sorted(depot_reports, key=_priority_key, reverse=True)
        ilk3 = ", ".join(
            f"{r.depot_name or r.depot_id} ({r.critical_count} kritik)"
            for r in sirali[:3]
        )
        return (
            f"Türkiye geneli: {toplam_depo} depo değerlendirildi, "
            f"toplam {toplam_kritik} kritik kalem. "
            f"Öncelikli depolar: {ilk3 or 'yok'}."
        )


class _ClaudeMetaSummary:
    SYSTEM = (
        "Sen B2 Cargo Türkiye geneli lojistik operasyon yöneticisisin. "
        "11 deponun risk raporundan kısa bir Türkçe yönetici özeti yaz. "
        "Hangi depolara öncelik verilmeli, net söyle. En fazla 6 cümle."
    )

    def __init__(self, client: ClaudeClient | None = None) -> None:
        self._client = client or ClaudeClient()

    def generate(self, depot_reports: list[DepotRiskReport]) -> str:
        sirali = sorted(depot_reports, key=_priority_key, reverse=True)
        satir = "\n".join(
            f"- {r.depot_name or r.depot_id}: {r.critical_count} kritik, "
            f"en yüksek skor {r.max_score:.0f}, {len(r.results)} kalem"
            for r in sirali
        )
        prompt = (
            f"Depo sayısı: {len(depot_reports)}\n"
            f"Depo bazlı durum (en riskliden aza):\n{satir}\n\n"
            "Türkiye geneli yönetici özeti yaz."
        )
        return self._client.generate(self.SYSTEM, prompt, max_tokens=1024)


class MetaAgent:
    def __init__(
        self,
        claude_summary: _ClaudeMetaSummary | None = None,
        template_summary: _TemplateMetaSummary | None = None,
    ) -> None:
        self._claude = claude_summary or _ClaudeMetaSummary()
        self._template = template_summary or _TemplateMetaSummary()

    def consolidate(self, depot_reports: list[DepotRiskReport]) -> TurkeyWideReport:
        prioritized = [
            r.depot_id
            for r in sorted(depot_reports, key=_priority_key, reverse=True)
        ]
        summary = (
            safe_run_agent(
                self._claude.generate,
                self._template.generate,
                depot_reports=depot_reports,
            )
            or ""
        )
        return TurkeyWideReport(
            depot_reports=depot_reports,
            executive_summary=summary,
            prioritized_depots=prioritized,
        )
