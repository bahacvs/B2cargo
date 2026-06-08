"""Claude API ince sarmalayıcı — ExplanationAgent / ActionAgent / MetaAgent paylaşır.

Tasarım: anthropic SDK ve ANTHROPIC_API_KEY yoksa `LLMUnavailable` fırlatır;
böylece `safe_run_agent` template fallback'e düşer (CLAUDE.md "Claude başarısız →
template" kuralı). Model `ANTHROPIC_MODEL` ortam değişkeninden gelir (varsayılan:
claude-sonnet-4-6) — istenirse Opus'a alınabilir.
"""

from __future__ import annotations

import os

DEFAULT_MODEL = "claude-sonnet-4-6"


class LLMUnavailable(RuntimeError):
    """anthropic SDK / API anahtarı yok ya da çağrı başarısız."""


class ClaudeClient:
    """Tek bir Türkçe metin üretimi için minimal Messages API sarmalayıcı."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self._client = None

    def _ensure_client(self):
        if self._client is not None:
            return self._client
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise LLMUnavailable("ANTHROPIC_API_KEY tanımlı değil.")
        try:
            import anthropic  # lazy: opsiyonel bağımlılık
        except ImportError as exc:  # pragma: no cover - ortam bağımlı
            raise LLMUnavailable("anthropic SDK kurulu değil.") from exc
        self._client = anthropic.Anthropic()
        return self._client

    def generate(self, system: str, prompt: str, max_tokens: int = 1024) -> str:
        """Verilen system + prompt ile Türkçe metin üretir, düz metin döner."""

        client = self._ensure_client()
        try:
            # Adaptive thinking: konsolidasyon/özet akıl yürütme gerektirebilir.
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                thinking={"type": "adaptive"},
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:  # noqa: BLE001 - her hata fallback'i tetikler
            raise LLMUnavailable(f"Claude çağrısı başarısız: {exc}") from exc

        parts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
        text = "\n".join(parts).strip()
        if not text:
            raise LLMUnavailable("Claude boş yanıt döndürdü.")
        return text
