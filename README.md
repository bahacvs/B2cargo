# Axiom Logistics Intelligence

B2 Cargo'nun Türkiye genelindeki 11 deposunu ve araç filolarını izleyen,
kalem bazlı risk üreten, Meta-Agent ile Türkiye geneli konsolide rapor sunan
çok-ajanlı lojistik zekâ sistemi.

> Axiom'un kurumsal SaaS ürünü. B2 Cargo pilot müşteri.
> Mimari ve kurallar için bkz. [`CLAUDE.md`](./CLAUDE.md).

## Durum

Bu repo **iskelet + deterministik çekirdek** aşamasındadır:

| Adım | Bileşen | Durum |
|------|---------|-------|
| 1 | Pydantic modeller (`models/`) | ✅ Tamam |
| 2 | Mock adapters (`adapters/*/mock.py`) | ✅ Tamam |
| 3 | DB schema (`db/schema.sql`) | ✅ Tamam |
| 4 | TemperatureMonitorAgent | ✅ Tamam (sıfır AI) |
| 5 | StockRiskAgent | ✅ Tamam (deterministik) |
| 6 | Unit testler | ✅ 15+ senaryo |
| 7+ | Explanation/Action/Notification/Depot/Meta ajanları, scheduler, API, gerçek adapter'lar | 🚧 Stub (TODO) |

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
