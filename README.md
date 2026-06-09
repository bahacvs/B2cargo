# Axiom Logistics Intelligence

B2 Cargo'nun Türkiye genelindeki 11 deposunu ve araç filolarını izleyen,
kalem bazlı risk üreten, Meta-Agent ile Türkiye geneli konsolide rapor sunan
çok-ajanlı lojistik zekâ sistemi.

> Axiom'un kurumsal SaaS ürünü. B2 Cargo pilot müşteri.
> Mimari ve kurallar için bkz. [`CLAUDE.md`](./CLAUDE.md).

## Durum

Geliştirme Sırası 1–14 tamam:

| Adım | Bileşen | Durum |
|------|---------|-------|
| 1 | Pydantic modeller (`models/`) | ✅ Tamam |
| 2 | Mock adapters (`adapters/*/mock.py`) | ✅ Tamam |
| 3 | DB schema (`db/schema.sql`) | ✅ Tamam |
| 4 | TemperatureMonitorAgent | ✅ Tamam (sıfır AI) |
| 5 | StockRiskAgent | ✅ Tamam (deterministik) |
| 6 | Unit testler | ✅ 70+ test |
| 7 | ExplanationAgent (Claude + template fallback) | ✅ Tamam |
| 8 | ActionAgent (kural tabanlı + Claude notu) | ✅ Tamam |
| 9 | NotificationBuilder | ✅ Tamam |
| 10 | DepotAgent (config-driven birleştirici) | ✅ Tamam |
| 11 | MetaAgent (Türkiye geneli konsolidasyon) | ✅ Tamam |
| 12 | APScheduler (07:00 cron) | ✅ Tamam |
| 13 | FastAPI endpoints | ✅ Tamam |
| 14 | Gerçek adapter implementasyonları (httpx) | ✅ Tamam |
| — | DB persist katmanı (`db/connection.py`) | 🚧 Stub |

### API'yi çalıştır
```bash
USE_MOCK_ADAPTERS=true uvicorn api.main:app --reload
# GET /health  GET /reports/turkey  GET /reports/{depot_id}
# GET /notifications  POST /notifications/alert  {"depot_id":"ankara"}
```

### Scheduler
```python
from orchestration.scheduler import start_scheduler
start_scheduler()   # her gün 07:00 (Europe/Istanbul) run_daily_pipeline
```

> **Claude modeli:** ExplanationAgent/ActionAgent/MetaAgent `ANTHROPIC_MODEL`
> (varsayılan `claude-sonnet-4-6`) ve `ANTHROPIC_API_KEY` kullanır. Anahtar yoksa
> deterministik Türkçe template'lere düşer — sistem yine çalışır.

### Veri kaynağı & bildirim (güncel)
- **Stok/sevkiyat kaynağı: Omnia** (`STOCK_SOURCE=omnia`, varsayılan). Devambar artık
  yalnızca veritabanı — erişim sonra netleşecek. `StockAdapter` interface'i ikisini de
  kapsar; ajanlar/pipeline/dashboard değişmedi.
- **Bildirim teslimi: aciliyet skoruna göre WhatsApp / Telegram** (`delivery/`).
  Kritik → WhatsApp+Telegram, Yüksek → Telegram, günlük özet → Telegram.
  `USE_MOCK_NOTIFIERS=true` (varsayılan) gönderimi simüle eder; gerçek gönderim için
  `TELEGRAM_*` / `WHATSAPP_*` env değişkenleri.

## Hızlı Başlangıç

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # geliştirmede USE_MOCK_ADAPTERS=true yeter

USE_MOCK_ADAPTERS=true pytest tests/unit -v
```

## Mimari Özet

```
DepotAgent (11 instance, aynı kod, config-driven)
  ├── TemperatureMonitorAgent   → sıcaklık sapması (araç + depo)
  ├── StockRiskAgent            → kalem bazlı deterministik risk skoru
  ├── ExplanationAgent          → Claude API, Türkçe özet (+ fallback)
  ├── ActionAgent               → kural tabanlı + Claude API
  └── NotificationBuilder       → payload üretimi
MetaAgent → 11 depo raporunu birleştirir, Türkiye geneli executive summary
```

Yeni depo eklemek = `config/depots.yaml`'a bir blok. Python dosyası değişmez.
