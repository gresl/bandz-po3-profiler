-- REVIEW/STAGING ONLY. Do not run against production without P3 deployment review.
-- Isolated schema. No changes to existing normalized_events, alert_sources, etc.
BEGIN;
CREATE SCHEMA IF NOT EXISTS bandz_ingest;
CREATE TABLE IF NOT EXISTS bandz_ingest.sources (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_name text NOT NULL UNIQUE,
    symbol text NOT NULL,
    chart_tf text NOT NULL CHECK (chart_tf = '15'),
    anchor_tf text NOT NULL CHECK (anchor_tf = '240'),
    engine text NOT NULL CHECK (engine IN ('V2', 'Legacy')),
    price_places smallint NOT NULL CHECK (price_places BETWEEN 0 AND 10),
    token_sha256 bytea NOT NULL UNIQUE CHECK (octet_length(token_sha256) = 32),
    enabled boolean NOT NULL DEFAULT false
);
CREATE TABLE IF NOT EXISTS bandz_ingest.deliveries (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id bigint NOT NULL REFERENCES bandz_ingest.sources(id),
    received_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    body bytea NOT NULL CHECK (octet_length(body) BETWEEN 1 AND 40960),
    body_sha256 bytea NOT NULL CHECK (octet_length(body_sha256) = 32),
    status text NOT NULL CHECK (status IN ('accepted','invalid','conflict','stale')),
    error_code text,
    bar_close_ms bigint,
    event_count integer,
    omitted_count integer,
    invalid_identity_count integer,
    UNIQUE (source_id, id)
);
CREATE INDEX IF NOT EXISTS bandz_deliveries_source_received
    ON bandz_ingest.deliveries (source_id, received_at DESC);
CREATE TABLE IF NOT EXISTS bandz_ingest.events (
    source_id bigint NOT NULL REFERENCES bandz_ingest.sources(id),
    event_id text NOT NULL,
    first_delivery_id bigint NOT NULL,
    observed_ms bigint NOT NULL,
    kind text NOT NULL,
    side text NOT NULL CHECK (side IN ('BULL','BEAR')),
    c2_id text,
    signal_id text,
    link_id text,
    bar_close_price numeric NOT NULL,
    event_json jsonb NOT NULL,
    PRIMARY KEY (source_id, event_id),
    FOREIGN KEY (source_id, first_delivery_id)
        REFERENCES bandz_ingest.deliveries(source_id, id)
);
CREATE INDEX IF NOT EXISTS bandz_events_source_close
    ON bandz_ingest.events (source_id, observed_ms);
CREATE INDEX IF NOT EXISTS bandz_events_source_link
    ON bandz_ingest.events (source_id, link_id) WHERE link_id IS NOT NULL;
CREATE TABLE IF NOT EXISTS bandz_ingest.delivery_events (
    source_id bigint NOT NULL,
    delivery_id bigint NOT NULL,
    event_id text NOT NULL,
    PRIMARY KEY (source_id, delivery_id, event_id),
    FOREIGN KEY (source_id, delivery_id)
        REFERENCES bandz_ingest.deliveries(source_id, id),
    FOREIGN KEY (source_id, event_id)
        REFERENCES bandz_ingest.events(source_id, event_id)
);
COMMIT;
