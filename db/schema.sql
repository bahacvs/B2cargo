-- Axiom Logistics Intelligence — PostgreSQL + pgvector (Supabase)
-- docker-compose db servisi başlatıldığında otomatik uygulanır.

CREATE EXTENSION IF NOT EXISTS vector;

-- Kalem bazlı anlık stok görüntüleri
CREATE TABLE IF NOT EXISTS stock_snapshots (
    id           BIGSERIAL PRIMARY KEY,
    depot_id     TEXT        NOT NULL,
    item_id      TEXT        NOT NULL,
    sku          TEXT,
    name         TEXT        NOT NULL,
    category     TEXT,
    quantity     NUMERIC,
    unit         TEXT,
    temp_min_c   NUMERIC,                 -- null ise sıcaklık izlenmez
    temp_max_c   NUMERIC,
    zone_id      TEXT,
    shipment_id  TEXT,
    vehicle_id   TEXT,
    expiry_date  DATE,
    taken_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_stock_depot_taken ON stock_snapshots (depot_id, taken_at DESC);

-- Depo zon sıcaklıkları (Sensor)
CREATE TABLE IF NOT EXISTS depot_zone_temps (
    id           BIGSERIAL PRIMARY KEY,
    depot_id     TEXT        NOT NULL,
    zone_id      TEXT        NOT NULL,
    temp_c       NUMERIC     NOT NULL,
    measured_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_zone_depot_measured ON depot_zone_temps (depot_id, zone_id, measured_at DESC);

-- Araç sıcaklık + konum (Arvento)
CREATE TABLE IF NOT EXISTS vehicle_readings (
    id           BIGSERIAL PRIMARY KEY,
    vehicle_id   TEXT        NOT NULL,
    shipment_id  TEXT,
    depot_id     TEXT,
    lat          NUMERIC,
    lon          NUMERIC,
    temp_c       NUMERIC,
    speed_kmh    NUMERIC,
    measured_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_vehicle_measured ON vehicle_readings (vehicle_id, measured_at DESC);

-- Kalem/sevkiyat risk sonuçları
CREATE TABLE IF NOT EXISTS risk_assessments (
    id           BIGSERIAL PRIMARY KEY,
    depot_id     TEXT        NOT NULL,
    item_id      TEXT        NOT NULL,
    score        NUMERIC     NOT NULL,
    level        TEXT        NOT NULL,   -- CRITICAL/HIGH/MEDIUM/LOW
    reasons      JSONB       NOT NULL DEFAULT '[]',
    assessed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_risk_depot_assessed ON risk_assessments (depot_id, assessed_at DESC);

-- Her pipeline çalışması (audit trail)
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id           BIGSERIAL PRIMARY KEY,
    kind         TEXT        NOT NULL,   -- daily / alert
    started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at  TIMESTAMPTZ,
    status       TEXT        NOT NULL DEFAULT 'running',
    depot_id     TEXT,                   -- null = Türkiye geneli
    error        TEXT,
    details      JSONB       NOT NULL DEFAULT '{}'
);

-- Bildirim kuyruğu
CREATE TABLE IF NOT EXISTS notifications (
    id           BIGSERIAL PRIMARY KEY,
    depot_id     TEXT        NOT NULL,
    level        TEXT        NOT NULL,
    channel      TEXT        NOT NULL,   -- whatsapp/email/dashboard
    payload      JSONB       NOT NULL,
    status       TEXT        NOT NULL DEFAULT 'pending',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ML için veri biriktirme (pgvector embedding kolonu)
CREATE TABLE IF NOT EXISTS feature_logs (
    id           BIGSERIAL PRIMARY KEY,
    depot_id     TEXT        NOT NULL,
    item_id      TEXT,
    features     JSONB       NOT NULL DEFAULT '{}',
    embedding    vector(1536),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
