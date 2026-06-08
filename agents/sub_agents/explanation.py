"""ExplanationAgent — Türkçe risk özeti (Claude API + template fallback). Adım 7.

Kural (CLAUDE.md): Claude başarısız olursa `TemplateExplanation` kullanılır.
DepotAgent bu iki sınıfı `safe_run_agent(agent_fn=..., fallback_fn=...)` ile sarar.
"""

from __future__ import annotations

from collections import Counter

from agents.llm import ClaudeClient
from models.risk import RiskLevel, RiskResult

_LEVEL_TR = {
    RiskLevel.CRITICAL: "kritik",
    RiskLevel.HIGH: "yüksek",
    RiskLevel.MEDIUM: "orta",
    RiskLevel.LOW: "düşük",
}


def _level_counts(results: list[RiskResult]) -> Counter:
    return Counter(r.level for r in results)


def _top_items(results: list[RiskResult], n: int = 5) -> list[RiskResult]:
    risky = [r for r in results if r.level is not RiskLevel.LOW]
    return sorted(risky, key=lambda r: r.score, reverse=True)[:n]


class TemplateExplanation:
    """AI olmadan deterministik Türkçe özet — fallback ve test için."""

    def generate(self, depot_name: str, results: list[RiskResult]) -> str:
        counts = _level_counts(results)
        toplam = len(results)
        c = counts[RiskLevel.CRITICAL]
        y = counts[RiskLevel.HIGH]
        o = counts[RiskLevel.MEDIUM]

        if c == 0 and y == 0 and o == 0:
            return (
                f"{depot_name}: {toplam} kalemin tamamı normal. "
                "Kritik, yüksek veya orta riskli kalem yok."
            )

        satirlar = [
            f"{depot_name}: {toplam} kalem değerlendirildi — "
            f"{c} kritik, {y} yüksek, {o} orta risk."
        ]
        for r in _top_items(results):
            kodlar = ", ".join(reason.code for reason in r.reasons)
            satirlar.append(
                f"  - {r.item_id} ({_LEVEL_TR[r.level]}, skor {r.score:.0f}): {kodlar}"
            )
        return "\n".join(satirlar)


class ExplanationAgent:
    """Claude API ile akıcı Türkçe özet üretir."""

    SYSTEM = (
        "Sen B2 Cargo lojistik deposu için risk analisti bir asistansın. "
        "Verilen kalem risk listesinden kısa, net, eyleme dönük bir Türkçe "
        "özet yaz. Abartma, sadece veriye dayan. En fazla 5 cümle."
    )

    def __init__(self, client: ClaudeClient | None = None) -> None:
        self._client = client or ClaudeClient()

    def generate(self, depot_name: str, results: list[RiskResult]) -> str:
        counts = _level_counts(results)
        top = _top_items(results)
        satir = "\n".join(
            f"- {r.item_id}: {r.level.value} (skor {r.score:.0f}), "
            f"gerekçeler: {', '.join(rr.code for rr in r.reasons)}"
            for r in top
        )
        prompt = (
            f"Depo: {depot_name}\n"
            f"Toplam kalem: {len(results)}\n"
            f"Dağılım: {counts[RiskLevel.CRITICAL]} kritik, "
            f"{counts[RiskLevel.HIGH]} yüksek, {counts[RiskLevel.MEDIUM]} orta, "
            f"{counts[RiskLevel.LOW]} düşük.\n"
            f"Öne çıkan riskli kalemler:\n{satir or '(yok)'}\n\n"
            "Bu deponun durumunu özetle."
        )
        return self._client.generate(self.SYSTEM, prompt)
