"""ActionAgent — kural tabanlı aksiyon önerisi (+ opsiyonel Claude notu). Adım 8.

Kural tabanlı çekirdek deterministik ve her zaman çalışır; gerekçe koduna göre
aksiyon üretir. Claude erişilebilirse kısa bir Türkçe öncelik notu ekler, erişilemezse
sessizce atlanır (aksiyonlar yine de döner — pipeline durmaz).
"""

from __future__ import annotations

from agents.llm import ClaudeClient, LLMUnavailable
from models.risk import RiskLevel, RiskResult

# Gerekçe kodu → önerilen aksiyon(lar). Eşikler/kurallar veriden, AI'dan değil.
_ACTIONS_BY_CODE: dict[str, list[str]] = {
    "temp_deviation_depot": [
        "Depo zonu soğutma sistemini denetle",
        "Kalemi uygun sıcaklık zonuna taşı",
    ],
    "temp_deviation_vehicle": [
        "Araç soğutma ünitesini kontrol et",
        "Sürücüyü bilgilendir, gerekirse sevkiyatı durdur",
    ],
    "expiry_passed": ["Kalemi imha/iade sürecine al"],
    "expiry_imminent": ["Öncelikli sevkiyat/satış planla"],
    "shipment_delay": ["Sevkiyatı hızlandır", "Müşteriyi gecikme hakkında bilgilendir"],
    "low_stock": ["Yeniden sipariş oluştur"],
}

# Seviyeye göre aksiyon önceliği (NotificationBuilder de bunu kullanabilir).
_PRIORITY = {
    RiskLevel.CRITICAL: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.MEDIUM: 3,
    RiskLevel.LOW: 4,
}


class ActionAgent:
    def __init__(self, client: ClaudeClient | None = None) -> None:
        self._client = client  # None ise Claude notu eklenmez

    def recommend(self, depot_name: str, results: list[RiskResult]) -> list[dict]:
        """Riskli kalemler için kural tabanlı aksiyon listesi döner (LOW hariç)."""

        recommendations: list[dict] = []
        for r in results:
            if r.level is RiskLevel.LOW:
                continue
            actions: list[str] = []
            for reason in r.reasons:
                for action in _ACTIONS_BY_CODE.get(reason.code, []):
                    if action not in actions:
                        actions.append(action)
            recommendations.append(
                {
                    "item_id": r.item_id,
                    "depot_id": r.depot_id,
                    "level": r.level.value,
                    "priority": _PRIORITY[r.level],
                    "actions": actions,
                }
            )

        recommendations.sort(key=lambda x: (x["priority"], -0))
        self._maybe_add_note(depot_name, recommendations)
        return recommendations

    def _maybe_add_note(self, depot_name: str, recommendations: list[dict]) -> None:
        """Claude erişilebilirse en öncelikli aksiyona kısa Türkçe not ekler."""

        if not self._client or not recommendations:
            return
        try:
            note = self._client.generate(
                "Sen lojistik operasyon danışmanısın. Tek cümlelik Türkçe öneri ver.",
                f"{depot_name} deposunda en öncelikli kalem {recommendations[0]['item_id']}, "
                f"önerilen aksiyonlar: {recommendations[0]['actions']}. "
                "Operasyon ekibine tek cümlelik öncelik notu yaz.",
                max_tokens=256,
            )
            recommendations[0]["note"] = note
        except LLMUnavailable:
            pass  # not opsiyonel; aksiyonlar zaten hazır
