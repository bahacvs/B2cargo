"""ActionAgent — kural tabanlı + Claude API ile aksiyon önerisi. STUB (adım 8)."""

from __future__ import annotations

from models.risk import RiskResult


class ActionAgent:
    def recommend(self, depot_id: str, results: list[RiskResult]) -> list[dict]:
        # TODO(adım 8): yüksek/kritik kalemler için kural tabanlı aksiyonlar,
        # gerekirse Claude API ile zenginleştirme.
        raise NotImplementedError("ActionAgent henüz uygulanmadı (adım 8).")
