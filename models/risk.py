"""Risk modelleri — deterministik skorlama.

Risk skoru AI tarafından uydurulmaz. Ağırlıklar ve eşikler
`config/risk_weights.yaml`'da tanımlıdır. `RiskLevel.from_score` skor→seviye
eşleştirmesinin TEK otoritesidir; eşikler dışarıdan (yaml) beslenir, default
değerler CLAUDE.md ile uyumludur.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# CLAUDE.md varsayılan eşikleri. config/risk_weights.yaml bunları override eder.
DEFAULT_THRESHOLDS: dict[str, float] = {
    "critical": 75,
    "high": 45,
    "medium": 25,
}


class RiskLevel(str, Enum):
    """Risk seviyesi. Skor→seviye eşlemesi `from_score`'da tek yerde."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    @classmethod
    def from_score(
        cls, score: float, thresholds: dict[str, float] | None = None
    ) -> "RiskLevel":
        """Sayısal skoru risk seviyesine çevirir.

        75+ KRİTİK / 45-74 YÜKSEK / 25-44 ORTA / 0-24 DÜŞÜK (varsayılan eşikler).
        """

        t = thresholds or DEFAULT_THRESHOLDS
        if score >= t["critical"]:
            return cls.CRITICAL
        if score >= t["high"]:
            return cls.HIGH
        if score >= t["medium"]:
            return cls.MEDIUM
        return cls.LOW


class RiskReason(BaseModel):
    """Skora katkıda bulunan tek bir gerekçe (örn. sıcaklık sapması, gecikme)."""

    code: str
    description: str
    weight: float = 0.0  # config/risk_weights.yaml'daki ham ağırlık
    points: float = 0.0  # bu gerekçenin skora fiili katkısı


class RiskResult(BaseModel):
    """Bir kalemin risk değerlendirme sonucu."""

    item_id: str
    depot_id: str
    score: float = 0.0
    level: RiskLevel = RiskLevel.LOW
    reasons: list[RiskReason] = Field(default_factory=list)

    def add_reason(self, reason: RiskReason) -> None:
        """Gerekçe ekler ve skoru/seviyeyi yeniden hesaplar (default eşiklerle).

        StockRiskAgent yaml eşikleriyle `recompute` çağırarak override edebilir.
        """

        self.reasons.append(reason)
        self.recompute()

    def recompute(self, thresholds: dict[str, float] | None = None) -> None:
        """Skoru gerekçelerin puan toplamından, seviyeyi eşiklerden günceller."""

        self.score = sum(r.points for r in self.reasons)
        self.level = RiskLevel.from_score(self.score, thresholds)
