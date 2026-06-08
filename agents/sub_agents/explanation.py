"""ExplanationAgent — Claude API ile Türkçe özet. STUB (adım 7).

Kural: Claude API başarısız olursa template fallback kullanılır
(safe_run_agent deseni). Bu sınıf yalnızca AI yolunu temsil eder; fallback
`TemplateExplanation` ile gelecek.
"""

from __future__ import annotations

from models.risk import RiskResult


class ExplanationAgent:
    def generate(self, depot_id: str, results: list[RiskResult]) -> str:
        # TODO(adım 7): anthropic client ile Türkçe özet üret.
        # Başarısızlıkta TemplateExplanation.generate(...) fallback kullanılır.
        raise NotImplementedError("ExplanationAgent henüz uygulanmadı (adım 7).")


class TemplateExplanation:
    """AI olmadan deterministik şablon özet — fallback."""

    def generate(self, depot_id: str, results: list[RiskResult]) -> str:
        # TODO(adım 7): kalem sayısı/seviye dağılımından Türkçe şablon metin üret.
        raise NotImplementedError("TemplateExplanation henüz uygulanmadı (adım 7).")
