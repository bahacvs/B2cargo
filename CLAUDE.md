# Axiom Logistics Intelligence — CLAUDE.md

## Proje Nedir

B2 Cargo'nun Türkiye genelindeki 11 deposunu ve tüm araç filolarını
izleyen, kalem bazlı risk üreten, Meta-Agent ile Türkiye geneli konsolide
rapor sunan çok-ajanlı lojistik zekâ sistemi.

Bu sistem Axiom'un kurumsal SaaS ürünüdür. B2 Cargo pilot müşteri.

---

## Veri Kaynakları — Adapter'lar

```
Omnia API      → stok, kalem, sevkiyat verisi (ANA kaynak — B2 Cargo Omnia'ya geçti)
Sensor API     → depo bölge sıcaklıkları (ayrı sistem, API var)
Arvento API    → araç anlık konum + araç içi sıcaklık
Devambar       → ARTIK sadece veritabanı (yönetim Omnia'da). Erişim sonra netleşecek.
```

**Stok kaynağı geçişi:** Yönetim tarafı yalnızca Omnia kullanacak; stok + sevkiyat
verisi Omnia'dan gelir. Devambar bir veritabanı olarak kalır (doğrudan DB mi, API mi
olduğu sonra netleşecek). `StockAdapter` interface'i her ikisini de kapsar; kaynak
`STOCK_SOURCE` env (varsayılan `omnia`) ile seçilir. Adapter interface'i değişmedi —
ajanlar/pipeline/dashboard hiç etkilenmedi.

**Kritik kural:** Her adapter'ın bir Mock versiyonu var.
Gerçek API bağlantısı olmadan geliştirme durmamalı.
Adapter interface'i değişmez, sadece implementasyon değişir.

```python
# Doğru kullanım:
adapter = DevambarAdapter()          # prod
adapter = MockDevambarAdapter()      # test / geliştirme

# İkisi de aynı interface'i implemente eder
```

---

## Temel Mimari Kural: 11 Ajan = 1 Kod

11 depo için 11 farklı dosya yazılmaz.
`DepotAgent` sınıfı config ile örneklenir:

```python
depot_agents = {
    depot_id: DepotAgent(config=DEPOT_CONFIGS[depot_id])
    for depot_id in ALL_DEPOT_IDS
}
```

Yeni depo eklemek = `config/depots.yaml`'a bir blok eklemek.
Hiçbir Python dosyası değişmez.

---

## Sıcaklık İzleme Kuralı

Devambar'dan gelen `temp_min_c` ve `temp_max_c` null ise → sıcaklık izlenmez.
Kuru gıda, ambalajlı ürün vb. otomatik olarak atlanır.
Config'de ürün kategorisi tanımlanmaz — Devambar zaten biliyor.

```python
def needs_temp_monitoring(item: StockItem) -> bool:
    return item.temp_min_c is not None and item.temp_max_c is not None
```

---

## İki Sıcaklık Boyutu

```
Araç sıcaklığı  → Arvento adapter → VehicleTemperatureReading
                  Sevkiyat süresince anlık izleme

Depo sıcaklığı  → Sensor adapter → DepotZoneTemperature
                  Depo bölgesi (zon) bazında izleme
                  Hangi ürün hangi zonda → Devambar'dan eşleştirme
```

---

## Ajan Hiyerarşisi

```
DepotAgent (11 instance, aynı kod)
  ├── TemperatureMonitorAgent   → sıcaklık sapması (araç + depo)
  ├── StockRiskAgent            → kalem bazlı risk skoru
  ├── ExplanationAgent          → Claude API, Türkçe özet
  ├── ActionAgent               → kural tabanlı + Claude API
  └── NotificationBuilder       → payload üretimi (kanal = aciliyet skoru)

Teslim (delivery/)            → payload'ı GÖNDERİR: WhatsApp / Telegram
                                Kritik → WhatsApp+Telegram, Yüksek → Telegram

MetaAgent
  → 11 depo raporunu birleştirir
  → Türkiye geneli executive summary üretir
  → Öncelikli depo sıralaması
```

---

## Risk Skoru — Deterministik

Risk skoru AI tarafından uydurulmaz.
Kurallar `config/risk_weights.yaml` dosyasında.
Eşikler değiştirilebilir, kod değişmez.

```
75+   = KRİTİK
45-74 = YÜKSEK
25-44 = ORTA
0-24  = DÜŞÜK
```

---

## Pipeline Akışı

### Günlük 07:00 (scheduled)
```
fetch_all_depots → for each depot:
  fetch_stock(Devambar)
  fetch_depot_temps(Sensor)
  fetch_vehicle_temps(Arvento)
  run_depot_agent(snapshot)
→ meta_agent.consolidate(all_depot_reports)
→ send_daily_report
```

### Anlık Alarm (event-driven)
```
temperature_event_received
→ check_threshold
→ if alert: run_alert_pipeline
→ build_notification_payload
```

---

## Hata Yönetimi — Pipeline Durmamalı

1 depo başarısız olursa diğer 10 devam eder.
Explanation Agent başarısız olursa template kullanılır.
Claude API başarısız olursa fallback text üretilir.
Her hata loglanır, pipeline_runs tablosuna kaydedilir.

```python
# Her ajan çağrısı bu pattern ile sarılır:
result = safe_run_agent(
    agent_fn=explanation_agent.generate,
    fallback_fn=template_explanation.generate,
    shipment=shipment
)
```

---

## Veritabanı

PostgreSQL + pgvector (Supabase)

Tablolar:
- `stock_snapshots`      → kalem bazlı anlık stok
- `depot_zone_temps`     → depo zon sıcaklıkları
- `vehicle_readings`     → araç sıcaklık + konum
- `risk_assessments`     → kalem/sevkiyat risk sonuçları
- `pipeline_runs`        → her pipeline çalışması (audit trail)
- `notifications`        → bildirim kuyruğu
- `feature_logs`         → ML için veri biriktirme

---

## Geliştirme Sırası (Kesinlikle Bu Sıra)

```
1. Models (Pydantic) — temeli at
2. Mock adapters — gerçek API beklenmeden çalış
3. DB schema + migration
4. TemperatureMonitorAgent (saf kural, sıfır AI)
5. StockRiskAgent (deterministik, sıfır AI)
6. Unit testler (15+ senaryo)
7. ExplanationAgent (Claude API + fallback)
8. ActionAgent
9. NotificationBuilder
10. DepotAgent (yukarıdakileri birleştirir)
11. MetaAgent
12. APScheduler (07:00 cron)
13. FastAPI endpoints
14. Gerçek adapter implementasyonları (API geldikçe)
```

---

## Test Gereksinimleri

Her agent için minimum 10 unit test.
Mock adapter her test senaryosunda kullanılır.
Kritik senaryo listesi:

```
✓ Donuk gıda sıcaklık minimum altında → critical
✓ Araç sıcaklığı hedef dışı, gecikme var → critical + gecikme
✓ Kuru gıda → sıcaklık izleme yok, diğer riskler çalışır
✓ Depo zonu sıcaklık sapması → depo risk
✓ Null sıcaklık gelirse → DataQualityAlert, pipeline devam
✓ Sensor API cevap vermezse → fallback, diğer risk sinyalleri işlenir
✓ Devambar API cevap vermezse → depot skip, meta-agent devam
✓ Claude API başarısız → template fallback kullanılır
✓ 1 depo çöker → diğer 10 devam eder
✓ Tüm kalemlerde normal → rapor üretilir, alarm yok
```

---

## Environment Variables

```
DATABASE_URL=postgresql://...
ANTHROPIC_API_KEY=sk-ant-...
DEVAMBAR_API_URL=https://...
DEVAMBAR_API_KEY=...
SENSOR_API_URL=https://...
SENSOR_API_KEY=...
ARVENTO_API_URL=https://...
ARVENTO_API_KEY=...
USE_MOCK_ADAPTERS=true          # geliştirme ortamında true
TIMEZONE=Europe/Istanbul
LOG_LEVEL=INFO
```
